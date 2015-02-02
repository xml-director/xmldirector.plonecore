# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

"""
A sample Dexterity content-type implementation using
all XML field types.
"""


from zope.interface import implements
from plone.dexterity.content import Item
from plone.supermodel import model

from xmldirector.plonecore.i18n import MessageFactory as _

from xmldirector.plonecore.dx import dexterity_base
from xmldirector.plonecore.dx.xml_binary import XMLBinary
from xmldirector.plonecore.dx.xml_image import XMLImage
from xmldirector.plonecore.dx.xml_field import XMLText
from xmldirector.plonecore.dx.xpath_field import XMLXPath


class IXMLDocument(model.Schema):

    xml_content = XMLText(
        title=_(u'XML Content'),
        required=False
    )

    xml_xpath = XMLXPath(
        title=_(u'XML XPath expression'),
        description=_(u'Format: field=<fieldname>,xpath=<xpath expression>'),
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


class XMLDocument(Item, dexterity_base.Mixin):

    implements(IXMLDocument)
