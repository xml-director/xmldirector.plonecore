################################################################
# zopyx.existdb
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################

from zope import schema
from zope.interface import Interface
from zopyx.existdb import MessageFactory as _


class IBrowserLayer(Interface):
    """A brower layer specific to my product """
   


class IExistDBSettings(Interface):
    """ ExistDB settings """

    existdb_url = schema.TextLine(
        title=_(u'eXistdb server url'),
        description=_(u'eXistdb base url'),
        default=u'http://localhost:6080',
        required=True,
    )

    existdb_username = schema.TextLine(
        title=_(u'eXistdb username '),
        description=_(u'eXistdb username'),
        default=u'admin',
        required=True,
    )

    existdb_password = schema.Password(
        title=_(u'eXistdb password'),
        description=_(u'eXistdb password'),
        default=u'',
        required=True,
    )

