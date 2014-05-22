################################################################
# zopyx.existdb
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################

from Products.Five.browser import BrowserView
from Products.ATContentTypes.interface.folder import IATFolder
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException

try:
    from plone.dexterity.interfaces import IDexterityContainer
    HAVE_DEXTERITY = True
except ImportError:
    HAVE_DEXTERITY = False

from ...logger import LOG
from ...interfaces import IPPContent, IArchiveFolder

def _c(s):
    if not isinstance(s, unicode):
        s = unicode(s, 'utf-8', 'ignore')
    return s.encode('utf-8')

class FlatHTMLView(BrowserView):
    """ A HTML collector for a Plone folder containing Document instances """

    def collect(self, published_only=False, filter_uids=[]):
        """ A collector taking only flat contents into account for the
            conversion.
        """

        def collect_objects(folder, level=0, items=[]):
            """ Collect all related subobjects """
            for brain in folder.getFolderContents({'sort_on' : 'getObjPositionInParent'}):
                obj = brain.getObject()

                if IPPContent.providedBy(obj):
                    items.append(dict(obj=obj, level=level))
                else:
                    LOG.warn('IPPContent not provided by %s' % obj.absolute_url(1))

                if HAVE_DEXTERITY:
                    if (IATFolder.providedBy(obj) or IDexterityContainer.providedBy(obj)) and not IArchiveFolder.providedBy(obj):
                        collect_objects(obj, level+1, items)
                else:
                    if IATFolder.providedBy(obj) and not IArchiveFolder.providedBy(obj):
                        collect_objects(obj, level+1, items)

        utils = getToolByName(self.context, 'plone_utils')
        wf_tool = getToolByName(self.context, 'portal_workflow')

        html = list()
        collected_objs = list()
        collect_objects(self.context, 0, collected_objs)
        for d in collected_objs:
            level = d['level']
            obj = d['obj']
            if filter_uids and not d['obj'].UID() in filter_uids:
                LOG.info('Filtered: %s' % obj.absolute_url(1))
                continue
            LOG.info('Introspecting %s' % obj.absolute_url(1))
            view = obj.restrictedTraverse('@@asHTML', None)
            if view is not None:
                pt = utils.normalizeString(obj.portal_type)
                review_state = wf_tool.getInfoFor(obj, 'review_state')
                if published_only and review_state not in ['published']:
                    continue
                html.append('<div class="mode-flat level-%d document-boundary portal-type-%s review-state-%s" path="%s" id="doc-id-%s" document_id="%s" review_state="%s" level="%d" uid="%s">\n' % 
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

        return '\n'.join(html)

    def __call__(self, published_only=False, filter_uids=[]):
        """ Collector for folderish content """
        return self.collect(published_only=published_only, filter_uids=filter_uids)
