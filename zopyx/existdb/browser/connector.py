import os
import re
import fs
import fs.errors
import fs.path
import urllib
import zipfile
import tempfile
import mimetypes
import logging
import zExceptions
import lxml.html
from fs.opener import opener
from fs.contrib.davfs import DAVFS
from fs.zipfs import ZipFS
from zope.interface import implements
from zope.interface import implementer
from zope.component import getUtility
from zope.publisher.interfaces import IPublishTraverse
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZPublisher.Iterators import IStreamIterator
from plone.registry.interfaces import IRegistry
from zopyx.existdb.interfaces import IExistDBSettings
from zopyx.existdb import MessageFactory as _


LOG = logging.getLogger('zopyx.existdb')


class webdav_iterator(file):

    implements(IStreamIterator)

    def __init__(self, handle, mode='rb', streamsize=1<<16):
        self.fp = handle.open('.', mode)
        self.streamsize = streamsize

    def next(self):
        data = self.fp.read(self.streamsize)
        if not data:
            raise StopIteration
        return data

    def __len__(self):
        cur_pos = self.fp.tell()
        self.fp.seek(0, 2)
        size = self.fp.tell()
        self.seek(cur_pos, 0)
        return size


class Precondition(object):

    def __init__(self, suffixes=[], view_names=[], view_handler=None):
        self.suffixes = suffixes
        self.view_names = view_names
        self.view_handler = view_handler

    def can_handle(self, filename, view_name):

        if view_name not in self.view_names:
            return False

        basename, suffix = os.path.splitext(filename)
        if suffix not in self.suffixes:
            return False

        return True
    
    def handle_view(self, webdav_handle, filename, view_name, request):
        return self.view_handler(webdav_handle, filename, view_name, request)


class PreconditionRegistry(object):

    def __init__(self):
        self._p = list()
        self._p_default = None

    def register(self, precondition, priority=None):
        self._p.append(precondition)

    def set_default(self, precondition):
        self._p_default = precondition

    def dispatch(self, webdav_handle, filename, view_name, request):
        
        for precondition in self._p:
            if precondition.can_handle(filename, view_name):
                return precondition.handle_view(webdav_handle, filename, view_name, request)

        if self._p_default:
            return self._p_default.handle_view(webdav_handle, filename, view_name, request)
        raise ValueError('No matching precondition found')
       

def default_html_handler(webdav_handle, filename, view_name, request):

    html_template = ViewPageTemplateFile('html_view.pt')

    # exist-db base url
    base_url = '{}/view/{}'.format(request.context.absolute_url(1), '/'.join(request.subpath[:-1]))

    # get HTML
    html = webdav_handle.open('.', 'rb').read()
    root = lxml.html.fromstring(html)

    # rewrite relative image urls
    for img in root.xpath('//img'):
        src = img.attrib['src']
        if not src.startswith('http'):
            img.attrib['src'] = '{}/{}'.format(base_url, src)

    # rewrite relative image urls
    for link in root.xpath('//link'):
        src = link.attrib['href']
        if not src.startswith('http'):
            link.attrib['href'] = '{}/{}'.format(base_url, src)

    html = lxml.html.tostring(root)
    return html_template.pt_render(dict(
                         template='html_view',
                         request=request,
                         context=request.context,
                         options=dict(
                             base_url=base_url,
                             html=html)))

def ace_editor(webdav_handle, filename, view_name, request, readonly=False, template_name='ace_editor.pt'):
    """ Default handler for showing/editing textish content through the ACE editor """

    mt, encoding = mimetypes.guess_type(filename)
    content = webdav_handle.open('.', 'rb').read()
    ace_mode = {'text/html': 'xml',
                'text/xml': 'xml',
                'text/css': 'css',
                'application/json': 'json',
            }.get(mt, 'text');
    template = ViewPageTemplateFile(template_name)
    action_url = '{}/view-editor/{}'.format(request.context.absolute_url(),
                                            '/'.join(request.subpath))
    return template.pt_render(dict(
                         template='ace_editor.pt',
                         request=request,
                         context=request.context,
                         options=dict(content=content, 
                                      action_url=action_url,
                                      readonly=readonly,
                                      ace_readonly=str(readonly).lower(), # JS
                                      ace_mode=ace_mode)))


def ace_editor_readonly(webdav_handle, filename, view_name, request, readonly=True, template_name='ace_editor.pt'):
    return ace_editor(webdav_handle, filename, view_name, request, readonly, template_name)


def default_view_handler(webdav_handle, filename, view_name, request):
    """ Default handler for images and other binary resources """

    info = webdav_handle.getinfo('.')
    mt, encoding = mimetypes.guess_type(filename)
    if not mt:
        mt = 'application/octet-stream'
    request.response.setHeader('Content-Type', mt)
    if 'size' in info:
        request.response.setHeader('Content-Length', info['size'])
        return webdav_iterator(webdav_handle)
    else:
        data = webdav_handle.open('.', 'rb').read()
        request.response.setHeader('Content-Length', len(data))
        return data


PC = PreconditionRegistry()
PC.register(Precondition(suffixes=['.html', '.htm'], view_names=['view'], view_handler=default_html_handler))
PC.register(Precondition(suffixes=['.html', '.htm', '.css', '.json'], view_names=['view-editor'], view_handler=ace_editor))
PC.register(Precondition(suffixes=['.html', '.htm', '.css', '.json'], view_names=['view-editor-readonly'], view_handler=ace_editor_readonly))
PC.set_default(Precondition(view_handler=default_view_handler))


@implementer(IPublishTraverse)
class Connector(BrowserView):

    view_name = 'view'
    template = ViewPageTemplateFile('connector_view.pt')

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.subpath = []

    @property
    def fs_handle(self):

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IExistDBSettings)

        url = '{}/exist/webdav/db'.format(settings.existdb_url)

        if self.context.existdb_subpath:
            url += '/{}'.format(self.context.existdb_subpath)
        if self.subpath:
            url += '/{}'.format(urllib.quote('/'.join(self.subpath)))

        try:
            return DAVFS(url, credentials=dict(username=settings.existdb_username,
                                                 password=settings.existdb_password))
        except fs.errors.ResourceNotFoundError:
            msg = 'eXist-db path {} does not exist'.format(url)
            self.context.plone_utils.addPortalMessage(msg, 'error')
            LOG.error(msg)
            raise zExceptions.NotFound()
        except fs.errors.PermissionDeniedError:
            msg = 'eXist-db path {} unauthorizd access (check credentials)'.format(url)
            self.context.plone_utils.addPortalMessage(msg, 'error')
            LOG.error(msg)
            raise zExceptions.Unauthorized()


    def redirect(self, message=None, level='info'):
        if message:
            self.context.plone_utils.addPortalMessage(message, level)
        return self.request.response.redirect(self.context.absolute_url())


    def __call__(self, *args, **kw):

        handle = self.fs_handle
        if handle.isdir('.'):
            files = handle.listdirinfo(files_only=True)
            files = [f for f in files if not f[0].startswith('.')]
            files = sorted(files)
            dirs = handle.listdirinfo(dirs_only=True)
            dirs = sorted(dirs)
            dirs = [d for d in dirs if not d[0].startswith('.')]
            return self.template(
                    subpath='/'.join(self.subpath),
                    files=files, 
                    dirs=dirs)

        elif handle.isfile('.'):
            filename = self.subpath[-1]
            self.request.subpath = self.subpath
            self.request.context = self.context
            return PC.dispatch(handle, filename, self.view_name, self.request)

        else:
            raise RuntimeError()

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    def searchabletext(self):
        """ Return indexable content """
        handle = self.fs_handle
        if 'index.html' in handle.listdir():
            with handle.open('index.html', 'rb') as fp:
                return fp.read()
        return None

    def reindex(self):
        """ Reindex current connector """
        self.context.reindexObject()
        self.context.log('Reindexed')
        return self.redirect(u'Reindex successfully')

    def clear_contents(self):
        """ Remove all sub content """

        handle = self.fs_handle
        for name in handle.listdir():
            if handle.isfile(name):
                handle.remove(name)
            else:
                handle.removedir(name, force=True, recursive=False)

        return self.redirect(_(u'eXist-db collection cleared'))

    def zip_export(self, download=True):
        """ Export WebDAV subfolder to a ZIP file """

        handle = self.fs_handle

        zip_filename = tempfile.mktemp(suffix='.zip')
        zf = zipfile.ZipFile(zip_filename, 'w')
        for dirname, filenames in handle.walk():
            if dirname.startswith('/'):
                dirname = dirname.lstrip('/')
            for filename in filenames:
                z_filename = fs.path.join(dirname, filename)
                with handle.open(z_filename, 'rb') as fp:
                    zf.writestr(z_filename, fp.read())
        zf.close()

        if download:
            self.request.response.setHeader('content-type', 'application/zip')
            self.request.response.setHeader('content-size', os.path.getsize(zip_filename))
            self.request.response.setHeader('content-disposition', 'attachment; filename={}.zip'.format(self.context.id))
            with open(zip_filename, 'rb') as fp:
                self.request.response.write(fp.read())
            os.unlink(zip_filename)
            return
        else:
            return zip_filename
        

    def zip_import(self, zip_file=None):
        """ Import WebDAV subfolder from an uploaded ZIP file """

        handle = self.fs_handle

        if not zip_file:
            zip_filename = self.request.zipfile.filename
            zip_file = self.request.zipfile
        else:
            zip_filename = open(zip_file, 'rb')

        with ZipFS(zip_file, 'r') as zip_handle:

            # Cleanup webdav directory first
            for name in handle.listdir():
                if handle.isfile(name):
                    handle.remove(name)
                else:
                    handle.removedir(name, force=True, recursive=False)
            self.context.log(u'Subdirectory clear (ZIP import)')

            # import all files from ZIP into WebDAV
            count = 0
            for name in zip_handle.walkfiles():
                dirname = '/'.join(name.split('/')[:-1])
                try:
                    handle.makedir(dirname, recursive=True, allow_recreate=True)
                except Exception as e:
                    LOG.error('Failed creating {} failed ({})'.format(dirname, e))
               
                out_fp = handle.open(name.lstrip('/'), 'wb') 
                zip_fp = zip_handle.open(name, 'rb')
                out_fp.write(zip_fp.read())
                count += 1
#                out_fp.close()
#                zip_fp.close()

        self.context.log(u'ZIP file imported ({}, {} files)'.format(zip_filename, count))
        return self.redirect(_(u'Uploaded ZIP archive imported'))

    def navigation_structure(self, level_offset=0, strip_leading_numbers=True):

        handle = self.fs_handle
        if not 'index.html' in handle.listdir():
            return []
        with handle.open('index.html', 'rb') as fp:
            content = fp.read()

        root = lxml.html.fromstring(content)
        result = []
        for node in root.xpath('//*[local-name() = "h1"  or local-name() = "h2" or local-name() = "h3" or local-name() = "h4" or local-name() = "h5"]'):  
            level = int(node.tag[1:]) - level_offset
            texts = node.xpath('./text()')
            texts = [t.strip() for t in texts]
            text = u' '.join(texts).strip()
            if strip_leading_numbers:
                reg = re.compile(r'^[\d\.]*\s', re.UNICODE)
                text = reg.sub('', text)
            result.append(dict(level=level, text=text))
        return result


class AceEditor(Connector):
    view_name = 'view-editor'

    def __call__(self, *args, **kw):
        method = self.request.method
        if method == 'GET':
            return super(AceEditor, self).__call__(*args, **kw)
        elif method == 'POST':
            handle = self.fs_handle
            with handle.open('.', 'wb') as fp:
                fp.write(self.request.data)
            return 'done'


class AceEditorReadonly(Connector):
    view_name = 'view-editor-readonly'


class Logging(BrowserView):

    template = ViewPageTemplateFile('connector_log.pt')

    def __call__(self):
        return self.template()
