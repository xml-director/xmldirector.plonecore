# -*- coding: utf-8 -*-

################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import plone.api
import datetime
from zope import schema
from zope.interface import implements
from plone.directives import form
from plone.dexterity.content import Container
from plone.supermodel import model
from zope.annotation.interfaces import IAnnotations
from persistent.list import PersistentList
from z3c.form.browser.select import SelectWidget

from zopyx.existdb.i18n import MessageFactory as _


LOG_KEY = 'zopyx.existdb.connector.log'


class IConnector(model.Schema):

    existdb_subpath = schema.TextLine(
        title=_(u'Subdirectory in Exist-DB'),
        description=_(u'Subdirectory in Exist-DB'),
        required=False
    )    


class Connector(Container):
    implements(IConnector)

    @property
    def logger(self):
        annotations = IAnnotations(self)
        if not LOG_KEY in annotations:
            annotations[LOG_KEY] = PersistentList()
        return annotations[LOG_KEY]

    def log(self, comment, level='info'):
        """ Add a log entry """

        logger = self.logger
        entry = dict(date=datetime.datetime.utcnow(),
                     username=plone.api.user.get_current().getUserName(),
                     level=level,
                     comment=comment)
        logger.append(entry)
        logger._p_changed = 1

