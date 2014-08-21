################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import fs
import datetime
import fs.errors
import fs.path
import humanize
import hurry.filesize
import zipfile
import tempfile
import mimetypes
import logging
import zExceptions
from dateutil import tz
from fs.zipfs import ZipFS
from zope.interface import implements
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from AccessControl.SecurityManagement import getSecurityManager
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore import permissions
from plone.app.layout.globals.interfaces import IViewView
from zopyx.existdb.i18n import MessageFactory as _

from view_registry import precondition_registry

import connector_views  # needed to initalize the registry
import config

LOG = logging.getLogger('zopyx.existdb')

TZ = os.environ.get('TZ', 'UTC')
LOG.info('Local timezone: {}'.format(TZ))


class Dispatcher(BrowserView):

    def __call__(self, *args, **kw):

        user = getSecurityManager().getUser()
        if user.has_permission(permissions.ModifyPortalContent, self.context):
            return self.request.response.redirect('{}/@@view'.format(self.context.absolute_url()))
        else:
            default_view = self.context.default_view_anonymous
            if default_view:
                return self.request.response.redirect('{}/{}'.format(self.context.absolute_url(), default_view))
            else:
                msg = _(u'No default view configured for anonymous visitors')
                self.context.plone_utils.addPortalMessage(msg, 'error')
                raise zExceptions.NotFound()


@implementer(IPublishTraverse)
class Connector(BrowserView):

    view_name = 'view'
    template = ViewPageTemplateFile('connector_view.pt')

    implements(IViewView)

    def __init__(self, context, request):
        super(Connector, self).__init__(context, request)
        self.subpath = []

    def webdav_handle(self, subpath=None, root=False):
        """ Returns a webdav handle for the current subpath """

        if not root:
            if not subpath:
                subpath = '/'.join(self.subpath)

        try:
            return self.context.webdav_handle(subpath)
        except fs.errors.ResourceNotFoundError as e:
            msg = 'eXist-db path {} does not exist'.format(e.url)
            self.context.plone_utils.addPortalMessage(msg, 'error')
            LOG.error(msg)
            raise zExceptions.NotFound()
        except fs.errors.PermissionDeniedError as e:
            msg = 'eXist-db path {} unauthorizd access (check credentials)'.format(e.url)
            self.context.plone_utils.addPortalMessage(msg, 'error')
            LOG.error(msg)
            raise zExceptions.Unauthorized()

    def webdav_handle_parent(self):
        return self.webdav_handle(root=True)

    def redirect(self, message=None, level='info'):
        if message:
            self.context.plone_utils.addPortalMessage(message, level)
        return self.request.response.redirect(self.context.absolute_url())


    def __call__(self, *args, **kw):

        handle = self.webdav_handle()

        if handle.isdir('.'):

            context_url = self.context.absolute_url()
            view_prefix = '@@view'
            edit_prefix = '@@view-editor'
            if self.subpath:
                view_prefix += '/' + '/'.join(self.subpath)
                edit_prefix += '/' + '/'.join(self.subpath)

            files = list()
            for info in handle.listdirinfo(files_only=True):
                if not info[0].startswith('.'):
                    files.append(dict(url='{}/{}/{}'.format(context_url, view_prefix, info[0]),
                                      edit_url='{}/{}/{}'.format(context_url, edit_prefix, info[0]),
                                      title=info[0],
                                      editable=self.is_ace_editable(info[0]),
                                      size=self.human_readable_filesize(info[1]['size']),
                                      modified=self.human_readable_datetime(info[1]['modified_time'])))

            dirs = list()
            for info in handle.listdirinfo(dirs_only=True):
                dirs.append(dict(url='{}/{}/{}'.format(context_url, view_prefix, info[0]),
                                 title=info[0],
                                 modified=self.human_readable_datetime(info[1]['modified_time'])))

            return self.template(
                    view_prefix=view_prefix,
                    subpath='/'.join(self.subpath),
                    files=files, 
                    dirs=dirs)

        elif handle.isfile('.'):
            filename = self.subpath[-1]
            self.request.subpath = self.subpath
            self.request.context = self.context
            return precondition_registry.dispatch(handle, filename, self.view_name, self.request)
        else:
            raise RuntimeError()

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    def is_ace_editable(self, name):
        """ check if the given filename is editable using ACE editor """
        mt, encoding = mimetypes.guess_type(name)
        return mt in config.ACE_MODES

    def human_readable_filesize(self, num_bytes):
        """ Return num_bytes as human readable representation """
        return hurry.filesize.size(num_bytes, hurry.filesize.alternative)

    def searchabletext(self):
        """ Return indexable content """
        handle = self.webdav_handle()
        if 'index.html' in handle.listdir():
            with handle.open('index.html', 'rb') as fp:
                return fp.read()
        return None

    def reindex(self):
        """ Reindex current connector """
        self.context.reindexObject()
        self.context.log('Reindexed')
        return self.redirect(u'Reindexing successfully')

    def datetime_tz(self, dt):
        """ Convert Python UTC datetime.datetime to Zope DateTime.DateTime """
        to_tz = tz.gettz(TZ)
        dt = dt.replace(tzinfo=tz.gettz('UTC'))
        return dt.astimezone(to_tz).strftime('%d.%m.%Y %H:%M:%Sh')

    def human_readable_datetime(self, dt):
        """ Convert with `dt` datetime string into a human readable
            representation using humanize module.
        """
        diff = datetime.datetime.utcnow() - dt
        return humanize.naturaltime(diff)

    def clear_contents(self):
        """ Remove all sub content """

        handle = self.webdav_handle()
        for name in handle.listdir():
            if handle.isfile(name):
                handle.remove(name)
            else:
                handle.removedir(name, force=True, recursive=False)

        return self.redirect(_(u'eXist-db collection cleared'))

    def zip_export(self, download=True):
        """ Export WebDAV subfolder to a ZIP file """

        handle = self.webdav_handle()

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
        

    def zip_import(self, zip_file=None, clean_directories=[]):
        """ Import WebDAV subfolder from an uploaded ZIP file """

        handle = self.webdav_handle()

        if not zip_file:
            zip_filename = self.request.zipfile.filename
            zip_file = self.request.zipfile
        else:
            zip_filename = zip_file
            zip_file = open(zip_file, 'rb')
            LOG.info('ZIP import ({})'.format(zip_filename))

        try:
            with ZipFS(zip_file, 'r') as zip_handle:
                # Cleanup webdav directory first
                for i, name in enumerate(handle.listdir()):
                    if name not in clean_directories:
                        continue
                    if handle.isfile(name):
                        handle.remove(name)
                    else:
                        handle.removedir(name, force=True, recursive=False)
                self.context.log(u'Subdirectory cleared (ZIP import)')

                # import all files from ZIP into WebDAV
                count = 0
                for i, name in enumerate(zip_handle.walkfiles()):
                    print i, name
                    dirname = '/'.join(name.split('/')[:-1])
                    try:
                        handle.makedir(dirname, recursive=True, allow_recreate=True)
                    except Exception as e:
                        LOG.error('Failed creating {} failed ({})'.format(dirname, e))
                   
                    LOG.info('ZIP filename({})'.format(name))
                    out_fp = handle.open(name.lstrip('/'), 'wb') 
                    zip_fp = zip_handle.open(name, 'rb')
                    out_fp.write(zip_fp.read())
                    count += 1
#                out_fp.close()
#                zip_fp.close()

        except fs.zipfs.ZipOpenError as e:
            msg = u'Error opening ZIP file: {}'.format(e)
            return self.redirect(msg, 'error')

        self.context.log(u'ZIP file imported ({}, {} files)'.format(zip_filename, count))
        return self.redirect(_(u'Uploaded ZIP archive imported'))


class AceEditor(Connector):
    view_name = 'view-editor'

    def __call__(self, *args, **kw):
        method = self.request.method
        if method == 'GET':
            return super(AceEditor, self).__call__(*args, **kw)
        elif method == 'POST':
            handle = self.webdav_handle_parent()
            with handle.open(self.subpath[-1], 'wb') as fp:
                fp.write(self.request.data)
            return 'done'


class AceEditorReadonly(Connector):
    view_name = 'view-editor-readonly'


class Logging(BrowserView):

    template = ViewPageTemplateFile('connector_log.pt')

    def log_clear(self):
        """ Clear connector persistent log """
        self.context.log_clear()
        msg = u'Log entries cleared'
        self.context.plone_utils.addPortalMessage(msg)
        return self.request.response.redirect('{}/@@view'.format(self.context.absolute_url()))

    def __call__(self):
        return self.template()
