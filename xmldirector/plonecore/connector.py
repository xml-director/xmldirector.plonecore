# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import fs
import fs.errors
import urllib

import zExceptions
from zope import schema
from zope.interface import implements
from zope.component import getUtility
from plone.dexterity.content import Item
from plone.supermodel import model
from plone.registry.interfaces import IRegistry

from xmldirector.plonecore.i18n import MessageFactory as _
from xmldirector.plonecore.davfs import DAVFSWrapper as DAVFS
from xmldirector.plonecore.interfaces import IWebdavSettings

from xmldirector.plonecore.logger import LOG


class IConnector(model.Schema):

    webdav_subpath = schema.TextLine(
        title=_(u'Subdirectory in Exist-DB'),
        description=_(u'Subdirectory in Exist-DB'),
        required=False
    )

    webdav_username = schema.TextLine(
        title=_(u'(optional) username overriding the system settings'),
        required=False
    )

    webdav_password = schema.TextLine(
        title=_(u'(optional) password overriding the system settings'),
        required=False
    )

    api_enabled = schema.Bool(
        title=_(u'Public web API enabled'),
        default=False,
        required=False
    )

    default_view_anonymous = schema.TextLine(
        title=_(u'Default view (anonymous)'),
        description=_(
            u'Name of a default view for site visitors without edit permission'),
        required=False,
        default=None,
    )

    default_view_authenticated = schema.TextLine(
        title=_(u'Default view (authenticated)'),
        description=_(u'Name of a default view for anonymous site visitors'),
        required=False,
        default=u'@@view',
    )


class Connector(Item):

    implements(IConnector)

    webdav_url = None
    webdav_username = None
    webdav_password = None
    webdav_subpath = None

    def webdav_handle(self, subpath=None):
        """ Return WebDAV handle to root of configured connector object
            including configured webdav_subpath.
        """

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IWebdavSettings)

        adapted = IConnector(self)

        url = adapted.webdav_url or settings.webdav_url

        if adapted.webdav_subpath:
            url += '/{}'.format(adapted.webdav_subpath)

        if subpath:
            url += '/{}'.format(urllib.quote(subpath))

        # system-wide credentials
        username = settings.webdav_username
        password = settings.webdav_password or ''

        # local credentials override the system credentials
        if adapted.webdav_username and adapted.webdav_password:
            username = adapted.webdav_username
            password = adapted.webdav_password or ''

        try:
            return DAVFS(url, credentials=dict(username=username,
                                               password=password))
        except fs.errors.ResourceNotFoundError:
            LOG.error(u'Error accessing {}::{}::{}'.format(self.absolute_url(), url, self.REQUEST.get('HTTP_USER_AGENT')), exc_info=True)
            raise zExceptions.Unauthorized(url)
        except Exception as e:
            LOG.error(u'Error accessing {}::{}::{}'.format(self.absolute_url(), url, self.REQUEST.get('HTTP_USER_AGENT')), exc_info=True)
            e.url = url
            raise e
