
import fs
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
        url = self.context.url + '/' + '/'.join(self.subpath)
        handle = DAVFS(url, credentials=dict(username='admin', password='pnmaster'))
        if handle.isdir('.'):
            files = handle.listdirinfo(files_only=True)
            dirs = handle.listdirinfo(dirs_only=True)
            return self.template(
                    subpath='/'.join(self.subpath),
                    files=files, 
                    dirs=dirs)
        elif handle.isfile('.'):
            filename = self.subpath[-1]
            disposition = 'inline'
            mt = 'application/octetstream'
            if filename.endswith('.html'):
                mt = 'text/html'
            elif filename.endswith('.css'):
                mt = 'text/css'
            elif filename.endswith('.png'):
                mt = 'image/png'
            elif filename.endswith('.gif'):
                mt = 'image/gif'
            elif filename.endswith('.jpg'):
                mt = 'image/jpeg'
            else:
                disposition = 'attachment'
            data = handle.open('.', 'rb').read()
            self.request.response.setHeader('Content-Type', mt)
            self.request.response.setHeader('Content-Length', str(len(data)))
            if disposition == 'attachment':
                self.request.response.setHeader('content-disposition', 'attachment; filename={}'.format(filename))
            return data
        else:
            raise RuntimeError()

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self
