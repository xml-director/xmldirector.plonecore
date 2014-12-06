################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import uuid
import hashlib
import plone.api
import lxml.etree
from fs.contrib.davfs import DAVFS

from zopyx.existdb.i18n import MessageFactory as _
from zopyx.existdb.interfaces import IExistDBSettings

import plone.supermodel.exportimport
from plone.registry.interfaces import IRegistry
from plone.schemaeditor.fields import FieldFactory
from plone.schemaeditor.interfaces import IFieldFactory

import zope.schema
import zope.interface
import zope.component
from zope.schema import Text
from zope.schema import TextLine
from zope.schema.interfaces import IField
from zope.component import getUtility
from zope.security.interfaces import ForbiddenAttribute
from zope.security.checker import canAccess, canWrite, Proxy
from plone.namedfile.field import NamedBlobFile
from z3c.form import interfaces
from z3c.form.datamanager import DataManager

from z3c.form.widget import FieldWidget

import lxml

import zope.component
import zope.interface
import zope.schema
import zope.schema.interfaces
import zope.i18nmessageid

from z3c.form import widget

from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IValidator
from z3c.form.interfaces import IValue
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IDataManager
from z3c.form import widget
from z3c.form import validator
from z3c.form import converter
from z3c.form.browser import text
from zope.interface import implementsOnly, implementer
from zope.component import adapter
from zope.component import getUtility


from z3c.form.interfaces import IWidget
from plone.dexterity.interfaces import IDexterityFTI
from plone.behavior.interfaces import IBehaviorAssignable


################################################################
# XPath field
################################################################

class IXMLXPath(IField):
    """ Marker for XML fields """
    pass


class XMLXPath(TextLine):
    zope.interface.implements(IXMLXPath)


XMLXPathFactory = FieldFactory(XMLXPath, _(u'label_xml_xpath_field', default=u'XMLPath'))
XMLXPathHandler = plone.supermodel.exportimport.BaseHandler(XMLXPath)

from zopyx.existdb.dx.xml_field import XMLFieldDataManager

class IXPathWidget(IWidget):
    pass


class XPathWidget(text.TextWidget):
    """ Widget for XPath expressions."""
    zope.interface.implementsOnly(IXPathWidget)

    def xpath_to_value(self):

        # collect all fields (schema and behavior fields)
        schema = zope.component.getUtility(
            IDexterityFTI, name=self.context.portal_type).lookupSchema()
        fields = dict((fieldname, schema[fieldname]) for fieldname in schema)

        assignable = IBehaviorAssignable(self.context)
        for behavior in assignable.enumerateBehaviors():
            behavior_schema = behavior.interface
            fields.update((name, behavior_schema[name]) for name in behavior_schema)

        if not self.value:
            error = u'Empty XPath field specification'
            return dict(errors=[error], data=None)

        # parse our mini language (fix this)
        parts = self.value.split(',', 1)
        fieldname = parts[0].split('=')[1]
        xpath_expr = parts[1].split('=')[1]
        xml_field = fields.get(fieldname)
        if not xml_field: 
            error = u'No such field "{}"'.format(fieldname)
            return dict(errors=[error], data=None)

        # get the dedicated datamanager for the XMLText field
        # that knows how to pull data from the database
        adapter = XMLFieldDataManager(context=self.context, field=xml_field)
        xml = adapter.get()
        root = lxml.etree.fromstring(xml)

        # apply xpath expression
        try:
            result = root.xpath(xpath_expr)
        except lxml.etree.XPathEvalError as e:
            error = u'Invalid XPath expression "{}" (error: {})'.format(xpath_expr, e)
            return dict(errors=[error], data=None)

        return dict(errors=[], data=result)


@implementer(IFieldWidget)
@adapter(IXMLXPath, IFormLayer)
def XPathFieldWidget(field, request):
    """IFieldWidget factory for RecurrenceWidget."""
    return FieldWidget(field, XPathWidget(request))
