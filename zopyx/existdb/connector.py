# -*- coding: utf-8 -*-

from zope import schema
from zope.interface import implements
from plone.directives import form
from plone.dexterity.content import Container
from z3c.form.browser.select import SelectWidget
from plone.supermodel import model
from zopyx.existdb import MessageFactory as _


class IConnector(model.Schema):

    existdb_subpath = schema.TextLine(
        title=_(u'Subdirectory in Exist-DB'),
        description=_(u'Subdirectory in Exist-DB'),
        required=False
    )    


class Connector(Container):
    implements(IConnector)
