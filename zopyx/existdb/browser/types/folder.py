################################################################
# zopyx.existdb
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################

from Products.Five.browser import BrowserView
from Products.ATContentTypes.interface.folder import IATFolder
from Products.CMFCore.utils import getToolByName

try:
    from plone.dexterity.interfaces import IDexterityContainer
    HAVE_DEXTERITY = True
except ImportError:
    HAVE_DEXTERITY = False


from folder_flat import FlatHTMLView
from folder_nested import NestedHTMLView

class HTMLView(BrowserView):

    def __call__(self, published_only=False, filter_uids=[]):

        catalog = getToolByName(self.context, 'portal_catalog')
        # First check if there is a flat for a nested folder structure
        is_folderish = False
        for brain in catalog({'path' : '/'.join(self.context.getPhysicalPath())}):
            obj = brain.getObject()
            if obj == self.context:
                continue
            if HAVE_DEXTERITY:
                if (IATFolder.providedBy(obj) or IDexterityContainer.providedBy(obj)):
                    is_folderish = True
                    break
            else:
                if IATFolder.providedBy(obj):
                    is_folderish = True
                    break

        if is_folderish:
            return NestedHTMLView(request=self.request, context=self.context)(published_only, filter_uids)
        else:
            return FlatHTMLView(request=self.request, context=self.context)(published_only, filter_uids)
