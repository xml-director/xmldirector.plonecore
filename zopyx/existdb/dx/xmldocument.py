# -*- coding: utf-8 -*-

################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

from zope import schema
from zope.interface import implements
from plone.dexterity.content import Item
from plone.supermodel import model

from zopyx.existdb.i18n import MessageFactory as _

from xml_binary import XMLBinary
from xml_image import XMLImage
from xml_field import XMLText
from xpath_field import XMLXPath


class IXMLDocument(model.Schema):

    xml_content = XMLText(
        title=_(u'XML Content'),
        required=False
    )

    xml_xpath = XMLXPath(
        title=_(u'XML XPath expression'),
        required=False
    )

    xml_binary = XMLBinary(
        title=_(u'XML Binary'),
        required=False
    )

    xml_image = XMLImage(
        title=_(u'XML Image'),
        required=False
    )


class XMLDocument(Item):

    implements(IXMLDocument)
