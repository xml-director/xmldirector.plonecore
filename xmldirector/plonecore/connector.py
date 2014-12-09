# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import urllib
import plone.api
import datetime
from fs.contrib.davfs import DAVFS
from zope import schema
from zope.interface import implements
from zope.component import getUtility
from plone.dexterity.content import Item
from plone.supermodel import model
from plone.registry.interfaces import IRegistry
from zope.annotation.interfaces import IAnnotations
from persistent.list import PersistentList

from xmldirector.plonecore.interfaces import IExistDBSettings
from xmldirector.plonecore.i18n import MessageFactory as _


LOG_KEY = 'xmldirector.plonecore.connector.log'


class IConnector(model.Schema):

    existdb_subpath = schema.TextLine(
        title=_(u'Subdirectory in Exist-DB'),
        description=_(u'Subdirectory in Exist-DB'),
        required=False
    )

    existdb_username = schema.TextLine(
        title=_(u'(optional) username overriding the system settings'),
        required=False
    )

    existdb_password = schema.TextLine(
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

    existdb_url = None
    existdb_username = None
    existdb_password = None
    existdb_subpath = None


    @property
    def logger(self):
        annotations = IAnnotations(self)
        if LOG_KEY not in annotations:
            annotations[LOG_KEY] = PersistentList()
        return annotations[LOG_KEY]

    def log(self, comment, level='info', details=None):
        """ Add a log entry """

        logger = self.logger
        entry = dict(date=datetime.datetime.utcnow(),
                     username=plone.api.user.get_current().getUserName(),
                     level=level,
                     details=details,
                     comment=comment)
        logger.append(entry)
        logger._p_changed = 1

    def log_clear(self):
        """ Clear all logger entries """
        annotations = IAnnotations(self)
        annotations[LOG_KEY] = PersistentList()

    def webdav_handle(self, subpath=None):
        """ Return WebDAV handle to root of configured connector object
            including configured existdb_subpath.
        """

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IExistDBSettings)

        adapted = IConnector(self)

        url = adapted.existdb_url or settings.existdb_url

        if adapted.existdb_subpath:
            url += '/{}'.format(adapted.existdb_subpath)

        if subpath:
            url += '/{}'.format(urllib.quote(subpath))

        # system-wide credentials
        username = settings.existdb_username
        password = settings.existdb_password

        # local credentials override the system credentials
        if adapted.existdb_username and adapted.existdb_password:
            username = adapted.existdb_username
            password = adapted.existdb_password

        try:
            return DAVFS(url, credentials=dict(username=username,
                                               password=password))
        except Exception as e:
            e.url = url
            raise e
