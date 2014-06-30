# -*- coding: utf-8 -*-

################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

from zope import schema
from zope.interface import Interface
from zopyx.existdb.i18n import MessageFactory as _


class IBrowserLayer(Interface):
    """A brower layer specific to my product """
   


class IExistDBSettings(Interface):
    """ ExistDB settings """

    existdb_url = schema.TextLine(
        title=_(u'eXist-db server url'),
        description=_(u'eXist-db base url'),
        default=u'http://localhost:6080',
        required=True,
    )

    existdb_username = schema.TextLine(
        title=_(u'eXist-db username '),
        description=_(u'eXist-db username'),
        default=u'admin',
        required=True,
    )

    existdb_password = schema.Password(
        title=_(u'eXist-db password'),
        description=_(u'eXist-db password'),
        default=u'',
        required=True,
    )

