# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import implements
from plone.directives import form
from plone.dexterity.content import Container
from plone.supermodel import model
from zopyx.existdb import MessageFactory as _


class IConnector(model.Schema):

    url = schema.TextLine(
        title=_(u'label_existdb_url') ,
        description=_(u'help_existdb_url'),
        required=True
    )    


class Connector(Container):

    implements(IConnector)
