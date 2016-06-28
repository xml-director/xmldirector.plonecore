# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

from zope import schema
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from xmldirector.plonecore.i18n import MessageFactory as _


class IBrowserLayer(Interface):

    """A brower layer specific to my product """


class IConnectorHandle(Interface):

    """ Return a DAVFS handle for the system-wide configured conector handle """


class ITransformerRegistry(Interface):

    """ Marker interface for TransformerRegistry """


class IValidatorRegistry(Interface):

    """ Marker interface for ValidatorRegistry """


CONNECTOR_MODE_VOCAB = SimpleVocabulary([
    SimpleTerm(u'existdb', title=u'Exist-DB'),
    SimpleTerm(u'basex', title=u'BaseX'),
    SimpleTerm(u'alfresco', title=u'Alfresco'),
    SimpleTerm(u'dropbox-dropdav', title=u'Dropbox (via dropdav.com)'),
    SimpleTerm(u'owncloud', title=u'OwnCloud'),
    SimpleTerm(u'other', title=u'Other')
])


class IConnectorSettings(Interface):
    """ Connector settings """

    connector_url = schema.TextLine(
        title=_(u'Connection URL of storage'),
        description=_(u'WebDAV: http://host:port/path/to/webdav,'
                      'Local filesystem: file://path/to/directory, '
                      'AWS S3: s3://bucketname, SFTP sftp://host/path, '
                      'FTP: ftp://host/path'),
        default=u'',
        required=True
    )

    connector_username = schema.TextLine(
        title=_(u'Username for external storage'),
        description=_(u'Username'),
        default=u'admin',
        required=False
    )

    connector_password = schema.Password(
        title=_(u'Password external storage'),
        description=_(u'Password'),
        default=u'',
        required=False
    )

    connector_mode = schema.Choice(
        title=_(u'Connector mode'),
        description=_(u'Connector mode (defaults to \'Other\')'),
        default=u'other',
        required=True,
        vocabulary=CONNECTOR_MODE_VOCAB
    )

    connector_dexterity_subpath = schema.TextLine(
        title=_(u'Dexterity subpath'),
        description=_(u'Subpath inside storage for Dexterity content'),
        default=u'',
        required=False
    )

