################################################################
# zopyx.existdb
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################

from Products.Five.browser import BrowserView
from Products.ATContentTypes.interface.folder import IATFolder
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode
from pp.core.transformation import Transformer

try:
    from plone.dexterity.interfaces import IDexterityContainer
    HAVE_DEXTERITY = True
except ImportError:
    HAVE_DEXTERITY = False

from ...logger import LOG
from ...interfaces import IArchiveFolder

def _c(s):
    if not isinstance(s, unicode):
        s = unicode(s, 'utf-8', 'ignore')
    return s.encode('utf-8')

def collector(folder, level=1, published_only=False, html=[], filter_uids=[]):

    utils = getToolByName(folder, 'plone_utils')
    wf_tool = getToolByName(folder, 'portal_workflow')

    for brain in folder.getFolderContents({'sort_on' : 'getObjPositionInParent'}):
        obj = brain.getObject()
        LOG.info('Introspecting %s' % obj.absolute_url(1))
        view = obj.restrictedTraverse('@@asHTML', None)

        if view is not None:
            pt = utils.normalizeString(obj.portal_type)
            review_state = wf_tool.getInfoFor(obj, 'review_state')
            if published_only and review_state not in ['published']:
                continue

            is_folderish = False
            if HAVE_DEXTERITY:
                if (IATFolder.providedBy(obj) or IDexterityContainer.providedBy(obj)) and not IArchiveFolder.providedBy(obj):
                    is_folderish = True
            else:
                if IATFolder.providedBy(obj) and not IArchiveFolder.providedBy(obj):
                    is_folderish = True

            if is_folderish:
                html.append('<div class="mode-nested level-%d document-boundary portal-type-folder review-state-%s" path="%s" id="doc-id-%s" document_id="%s" review_state="%s" level="%d" uid="%s">\n' % 
                            (level, review_state, obj.absolute_url(1), obj.getId(), obj.getId(), review_state, level, obj.UID()))
                if IATFolder.providedBy(obj):
                    folder_title = obj.Title()
                    folder_descr = obj.Description()
                else:
                    folder_title = obj.title # Dexterity
                    folder_descr = obj.description
                html.append('<h%d class="title">%s</h%d>' % (level, folder_title, level))
                html.append('<div class="description">%s</div>' % folder_descr)
                collector(obj, level+1, published_only, html)
                html.append('</div>')

            else:
                html.append('<div class="level-%d document-boundary portal-type-%s review-state-%s" path="%s" id="doc-id-%s" document_id="%s" review_state="%s" level="%d" uid="%s">\n' % 
                            (level, pt, review_state, obj.absolute_url(1), obj.getId(), obj.getId(), review_state, level, obj.UID()))
                html.append('<div class="contentinfo">')
                html.append('<div><a class="editlink" href="%s/edit">Edit</a></div>' % obj.absolute_url())
                try:
                    html.append('<div class="review-state">%s</div>' % wf_tool.getInfoFor(obj, 'review_state'))
                except WorkflowException:
                    pass
                html.append('</div>')
                html.append(view())
                html.append('</div>')
        else :
            LOG.warn('No @@asHTML view found for %s' % obj.absolute_url(1))


class NestedHTMLView(BrowserView):
    """ A HTML collector for a Plone folder containing Document instances """

    def __call__(self, published_only=False, filter_uids=[]):
        """ Collector for folderish content """
        html = list()
        collector(self.context, 1, published_only, html, filter_uids=[])
        html = u'\n'.join([safe_unicode(item) for item in html])
        T = Transformer(['adjustHeadingsFromAggregatedHTML'])
        return T(html)

