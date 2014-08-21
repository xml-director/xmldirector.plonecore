# -*- coding: utf-8 -*-

################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import urllib
import plone.api
import datetime
from fs.contrib.davfs import DAVFS
from zope import schema
from zope.interface import implements
from zope.component import getUtility
from plone.dexterity.content import Container
from plone.supermodel import model
from plone.registry.interfaces import IRegistry
from zope.annotation.interfaces import IAnnotations
from persistent.list import PersistentList

from zopyx.existdb.interfaces import IExistDBSettings
from zopyx.existdb.i18n import MessageFactory as _


LOG_KEY = 'zopyx.existdb.connector.log'


class IConnector(model.Schema):

    existdb_subpath = schema.TextLine(
        title=_(u'Subdirectory in Exist-DB'),
        description=_(u'Subdirectory in Exist-DB'),
        required=False
    )    

    api_enabled = schema.Bool(
        title=_(u'Public web API enabled'),
        default=False,
        required=False
    )    

    default_view_anonymous = schema.TextLine(
        title=_(u'Default view'),
        description=_(u'Name of a default view for site visitors without edit permission'),
        required=False,
        default=None,
    )    

class Connector(Container):
    implements(IConnector)

    @property
    def logger(self):
        annotations = IAnnotations(self)
        if not LOG_KEY in annotations:
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

        url = '{}/exist/webdav/db'.format(settings.existdb_url)
        if self.existdb_subpath:
            url += '/{}'.format(self.existdb_subpath)

        if subpath:
            url += '/{}'.format(urllib.quote(subpath))

        try:
            return DAVFS(url, credentials=dict(username=settings.existdb_username,
                                               password=settings.existdb_password))
        except Exception as e:
            e.url = url
            raise e
