################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import json
import os
import uuid
import hashlib
import plone.api
import lxml.etree
from fs.contrib.davfs import DAVFS

import zope.schema
import zope.interface
import zope.component
from zope.schema.interfaces import IField
from zope.component import getUtility
from z3c.form.datamanager import AttributeField as AttributeDataManager
from plone.namedfile import NamedImage
from plone.namedfile.field import NamedImage as NamedImageField
import plone.supermodel.exportimport
from plone.registry.interfaces import IRegistry
from plone.schemaeditor.fields import FieldFactory

from zopyx.existdb.i18n import MessageFactory as _
from zopyx.existdb.interfaces import IExistDBSettings
from zopyx.existdb.dx.xml_binary import XMLBinaryDataManager


################################################################
# XML Image Content
################################################################

class IXMLImage(IField):
    """ Marker for XML fields """
    pass


class XMLImage(NamedImageField):
    zope.interface.implements(IXMLImage)


XMLImageFactory = FieldFactory(XMLImage, _(u'label_xml_Image_field', default=u'XMLImage'))
XMLImageHandler = plone.supermodel.exportimport.BaseHandler(XMLImage)


class XMLImageDataManager(XMLBinaryDataManager):
    """Attribute field."""
    zope.component.adapts(
        zope.interface.Interface, IXMLImage)

    suffix = '.img'

