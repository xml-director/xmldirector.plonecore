from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


@implementer(IPublishTraverse)
class Connector(BrowserView):

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.subpath = []

    __call__ = ViewPageTemplateFile('connector_view.pt')

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self
