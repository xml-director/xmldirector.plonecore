################################################################
# zopyx.existdb
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################

from ..compatible import InitializeClass
from Products.Five.browser import BrowserView

class HTMLView(BrowserView):
    """ This view renders a HMTL fragment for the configured content type """

    def collect(self, html):
        html.append('<div class="type-topic">')
        for brain in self.context.queryCatalog():
            obj = brain.getObject()
            view = obj.restrictedTraverse('@@asHTML', None)
            if view:
                html.append('<div class="topic-item">')
                html.append(view())
                html.append('</div>')
            else:
                html.append('<div class="topic-item">')
                html.append('<span class="aggregation-error">no view for %s (%s) found</span>' %
                            (obj.absolute_url(1), obj.portal_type))
                html.append('</div>')

        html.append('</div>')

    def __call__(self, *args, **kw):
        """ Collector for topic content """
        html = list()
        self.collect(html)
        return ''.join(html)

InitializeClass(HTMLView)

