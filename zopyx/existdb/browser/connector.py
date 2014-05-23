import fs
import urllib
import mimetypes
from fs.opener import opener
from fs.contrib.davfs import DAVFS
from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


@implementer(IPublishTraverse)
class Connector(BrowserView):
    
    template = ViewPageTemplateFile('connector_view.pt')

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.subpath = []

    def __call__(self, *args, **kw):
        url = self.context.url + '/' + urllib.quote('/'.join(self.subpath))
        handle = DAVFS(url, credentials=dict(username='admin', password='pnmaster'))
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
            info = handle.getinfo('.')
            mt, encoding = mimetypes.guess_type(filename)
            self.request.response.setHeader('Content-Type', mt)
            if 'size' in info:
                self.request.response.setHeader('Content-Length', info['size'])
            return handle.open('.', 'rb').read()
        else:
            raise RuntimeError()

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self
