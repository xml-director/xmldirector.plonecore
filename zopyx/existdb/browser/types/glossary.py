################################################################
# zopyx.existdb
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################

from ..compatible import InitializeClass
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ..util import getLanguageForObject
from ..sorting import sort_methods, default_sort_method

class GlossaryHTMLView(BrowserView):
    """ This view renders a HMTL fragment for the configured content type """

    template = ViewPageTemplateFile('glossary.pt')

    def getGlossaryDefinitions(self):

        language = getLanguageForObject(self.context)
        results = self.context.getCatalog()()
        results = [b.getObject() for b in results]
        sort_method = sort_methods.get(language)
        if sort_method:
            results.sort(sort_method)
        else:
            results.sort(default_sort_method)
        return results

    def __call__(self, *args, **kw):
        return self.template(self.context)

InitializeClass(GlossaryHTMLView)

