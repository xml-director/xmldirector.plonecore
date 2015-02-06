# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

from zope import schema
from zope.interface import Interface
from xmldirector.plonecore.i18n import MessageFactory as _


class IBrowserLayer(Interface):

    """A brower layer specific to my product """


class IWebdavHandle(Interface):

    """ Return a DAVFS handle for the system-wide configured
        WebDav/database server """


class IXSLTRegistry(Interface):

    """ Marker interface for XSLTRegistry """


class IValidatorRegistry(Interface):

    """ Marker interface for ValidatorRegistry """


class IWebdavSettings(Interface):

    """ ExistDB settings """

    webdav_url = schema.TextLine(
        title=_(u'WebDAV server url'),
        description=_(u'WebDAV base url'),
        default=u'http://localhost:6080/exist/webdav/db',
        required=True
    )

    webdav_dexterity_subpath = schema.TextLine(
        title=_(u'Dexterity WebDAV subpath'),
        description=_(u'Subpath inside WebDAV for Dexterity content'),
        default=u'',
        required=False
    )

    webdav_username = schema.TextLine(
        title=_(u'WebDAV username'),
        description=_(u'WebDAV username'),
        default=u'admin',
        required=True
    )

    webdav_password = schema.Password(
        title=_(u'WebDAV password'),
        description=_(u'WebDAV password'),
        default=u'',
        required=False
    )
