import fs
import fs.errors
import urllib
import mimetypes
import time
import zExceptions
import lxml.html
from fs.opener import opener
from fs.contrib.davfs import DAVFS
from zope.interface import implements
from zope.interface import implementer
from zope.component import getUtility
from zope.publisher.interfaces import IPublishTraverse
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZPublisher.Iterators import IStreamIterator
from plone.registry.interfaces import IRegistry
from zopyx.existdb.interfaces import IExistDBSettings


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


@implementer(IPublishTraverse)
class Connector(BrowserView):
    
    template = ViewPageTemplateFile('connector_view.pt')
    html_template = ViewPageTemplateFile('html_view.pt')

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.subpath = []

    def __call__(self, *args, **kw):

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IExistDBSettings)

        url = '{}/exist/webdav/db'.format(settings.existdb_url)

        if self.context.existdb_subpath:
            url += '/{}'.format(self.context.existdb_subpath)
        if self.subpath:
            url += '/{}'.format(urllib.quote('/'.join(self.subpath)))

        try:
            handle = DAVFS(url, credentials=dict(username=settings.existdb_username,
                                                 password=settings.existdb_password))
        except fs.errors.ResourceNotFoundError:
            raise zExceptions.NotFound()
            
        if handle.isdir('.'):

            files = handle.listdirinfo(files_only=True)
            files = sorted(files)
            dirs = handle.listdirinfo(dirs_only=True)
            dirs = sorted(dirs)
            return self.template(
                    subpath='/'.join(self.subpath),
                    files=files, 
                    dirs=dirs)

        elif handle.isfile('.'):

            filename = self.subpath[-1]
            if filename.endswith('.html'):
                return self.deliver_html(handle)

            info = handle.getinfo('.')
            mt, encoding = mimetypes.guess_type(filename)
            if not mt:
                mt = 'application/octet-stream'
            self.request.response.setHeader('Content-Type', mt)
            if 'size' in info:
                self.request.response.setHeader('Content-Length', info['size'])
                return webdav_iterator(handle)
            else:
                data = handle.open('.', 'rb').read()
                self.request.response.setHeader('Content-Length', len(data))
                return data
        else:
            raise RuntimeError()

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    def deliver_html(self, handle):

        print '-'*80
        ts = time.time()
        # exist-db base url
        base_url = '{}/view/{}'.format(self.context.absolute_url(1), '/'.join(self.subpath[:-1]))

        # get HTML
        html = handle.open('.', 'rb').read()
        print time.time() - ts
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
        print time.time() - ts
        return self.html_template(html=html)
