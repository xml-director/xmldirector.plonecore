# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


################################################################
# Patch for
# https://github.com/plone/Products.CMFPlone/issues/1527
################################################################

import json

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.controlpanel import ILinkSchema
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from Products.Five.browser.metaconfigure import ViewMixinForTemplates
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.globals.interfaces import ILayoutPolicy
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.icons.interfaces import IContentIcon
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.view import memoize
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer
from plone.registry.interfaces import IRegistry
from zope.browserpage.viewpagetemplatefile import (
    ViewPageTemplateFile as ZopeViewPageTemplateFile
)
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.browser import BrowserView


def bodyClass(self, template, view):
    """
    Returns the CSS class to be used on the body tag.

    Included body classes
    - template name: template-{}
    - portal type: portaltype-{}
    - navigation root: site-{}
    - section: section-{}
        - only the first section
    - section structure
        - a class for every container in the tree
    - hide icons: icons-on
    - markspeciallinks: pat-markspeciallinks
    - userrole-{} for each role the user has in this context
    - min-view-role: role required to view context
    - default-view: if view is the default view
    """
    context = self.context
    portal_state = getMultiAdapter(
        (context, self.request), name=u'plone_portal_state')
    normalizer = queryUtility(IIDNormalizer)

    body_classes = []
    # template class (required)
    name = ''
    if isinstance(template, ViewPageTemplateFile) or \
       isinstance(template, ZopeViewPageTemplateFile) or \
       isinstance(template, ViewMixinForTemplates):
        # Browser view
        name = view.__name__
    # fixes https://github.com/plone/Products.CMFPlone/issues/1527
    elif isinstance(template, str):
        name = template
    elif template is not None:
        name = template.getId()
    if name:
        name = normalizer.normalize(name)
        body_classes.append('template-%s' % name)

    # portal type class (optional)
    portal_type = normalizer.normalize(context.portal_type)
    if portal_type:
        body_classes.append("portaltype-%s" % portal_type)

    # section class (optional)
    navroot = portal_state.navigation_root()
    body_classes.append("site-%s" % navroot.getId())

    contentPath = context.getPhysicalPath()[
        len(navroot.getPhysicalPath()):]
    if contentPath:
        body_classes.append("section-%s" % contentPath[0])
        # skip first section since we already have that...
        if len(contentPath) > 1:
            registry = getUtility(IRegistry)
            depth = registry.get(
                'plone.app.layout.globals.bodyClass.depth', 4)
            if depth > 1:
                classes = ['subsection-%s' % contentPath[1]]
                for section in contentPath[2:depth]:
                    classes.append('-'.join([classes[-1], section]))
                body_classes.extend(classes)

    # class for hiding icons (optional)
    if self.icons_visible():
        body_classes.append('icons-on')
    else:
        body_classes.append('icons-off')

    # class for hiding thumbs (optional)
    if self.thumb_visible():
        body_classes.append('thumbs-on')
    else:
        body_classes.append('thumbs-off')

    # permissions required. Useful to theme frontend and backend
    # differently
    permissions = []
    if not getattr(view, '__ac_permissions__', tuple()):
        permissions = ['none']
    for permission, roles in getattr(view, '__ac_permissions__', tuple()):
        permissions.append(normalizer.normalize(permission))
    if 'none' in permissions or 'view' in permissions:
        body_classes.append('frontend')
    for permission in permissions:
        body_classes.append('viewpermission-' + permission)

    # class for user roles
    membership = getToolByName(context, "portal_membership")

    if membership.isAnonymousUser():
        body_classes.append('userrole-anonymous')
    else:
        user = membership.getAuthenticatedMember()
        for role in user.getRolesInContext(self.context):
            body_classes.append('userrole-' + role.lower().replace(' ', '-'))

        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISiteSchema, prefix='plone', check=False)

        # toolbar classes
        try:
            left = settings.toolbar_position == 'side'
        except KeyError:
            left = True
        if left:
            body_classes.append('plone-toolbar-left')
        else:
            body_classes.append('plone-toolbar-top')
        try:
            toolbar_state = self.request.cookies.get('plone-toolbar')
            if toolbar_state:
                toolbar_state = json.loads(toolbar_state)
            else:
                toolbar_state = {'expanded': True}
            if toolbar_state.get('expanded', True):
                body_classes.append('plone-toolbar-expanded')
                if left:
                    body_classes.append('plone-toolbar-left-expanded')
                else:
                    body_classes.append('plone-toolbar-top-expanded')
            else:
                if left:
                    body_classes.append('plone-toolbar-left-default')
                else:
                    body_classes.append('plone-toolbar-top-default')
        except:
            pass

    # class for markspeciallinks pattern
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ILinkSchema,
                                     prefix="plone",
                                     check=False)

    msl = settings.mark_special_links
    elonw = settings.external_links_open_new_window
    if msl or elonw:
        body_classes.append('pat-markspeciallinks')

    return ' '.join(body_classes)


from plone.app.layout.globals.layout import LayoutPolicy
LayoutPolicy.bodyClass = bodyClass
