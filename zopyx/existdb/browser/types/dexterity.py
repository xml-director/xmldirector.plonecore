################################################################
# zopyx.existdb
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################

from ..compatible import InitializeClass
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class DexterityGenericView(BrowserView):
    """ This is the most generic Dexertiy view that will be used
        for Dexterity-based content-types created throught-the-web
        which have no specific interfaces. Dexterity types
        defined through code usually have a specific interface
        and can be defined through the standard way as for other
        AT-based content-types.
    """

    template = ViewPageTemplateFile('dexterity.pt')

    def __call__(self, *args, **kw):
        return self.template(self.context)

InitializeClass(DexterityGenericView)

