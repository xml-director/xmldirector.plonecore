# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

from zope import schema
from zope.interface import Interface
from xmldirector.plonecore.i18n import MessageFactory as _
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class IBrowserLayer(Interface):
    """A brower layer specific to my product """


class IWebdavHandle(Interface):
    """ Return a DAVFS handle for the system-wide configured
        WebDav/database server """


class IExistDBSettings(Interface):
    """ ExistDB settings """

    existdb_url = schema.TextLine(
        title=_(u'eXist-db server url'),
        description=_(u'eXist-db base url'),
        default=u'http://localhost:6080/exist/webdav/db',
        required=True,
    )

    existdb_dexterity_subpath = schema.TextLine(
        title=_(u'Dexterity eXist-db subpath'),
        description=_(u'Subpath inside eXist-db for Dexterity content'),
        default=u'',
        required=False,
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
