################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import re
import plone.api
import lxml.etree

from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IFieldWidget
from z3c.form.browser import text
from z3c.form.interfaces import IWidget
from z3c.form.widget import FieldWidget
import zope.schema
import zope.schema.interfaces
import zope.interface
import zope.component
from zope.schema import TextLine
from zope.schema.interfaces import IField
import zope.i18nmessageid
from zope.interface import implementer
from zope.component import adapter
from plone.dexterity.interfaces import IDexterityFTI
from plone.behavior.interfaces import IBehaviorAssignable
import plone.supermodel.exportimport
from plone.schemaeditor.fields import FieldFactory

from xmldirector.plonecore.i18n import MessageFactory as _


regex = re.compile('field=([\w]*),xpath=(.*)', re.UNICODE)


def parse_field_expression(value):
    """ Parses a string like
        field=xmlfield, xpath=/a/b/c
    """
    if not value:
        return None

    mo = regex.match(value)
    if not mo:
        return None
    return mo.groups()


def get_all_fields(context):
    """ Return all fields (including behavior fields) of a context object
        as dict fieldname -> field.
    """

    schema = zope.component.getUtility(
        IDexterityFTI, name=context.portal_type).lookupSchema()
    fields = dict((fieldname, schema[fieldname]) for fieldname in schema)

    assignable = IBehaviorAssignable(context)
    for behavior in assignable.enumerateBehaviors():
        behavior_schema = behavior.interface
        fields.update((name, behavior_schema[name])
                      for name in behavior_schema)

    return fields


################################################################
# XPath field
################################################################

class IXMLXPath(IField):

    """ Marker for XML fields """
    pass


class XMLXPath(TextLine):
    zope.interface.implements(IXMLXPath)

    def validate(self, value):

        if value:
            mo = parse_field_expression(value)
            try:
                fieldname, xpath_expr = mo
            except TypeError:
                raise zope.interface.Invalid(
                    u'Invalid specification ({})'.format(value))
        return super(XMLXPath, self).validate(value)


XMLXPathFactory = FieldFactory(XMLXPath, _(
    u'label_xml_xpath_field', default=u'XML (extended XPath expression)'))
XMLXPathHandler = plone.supermodel.exportimport.BaseHandler(XMLXPath)

from xmldirector.plonecore.dx.xml_field import XMLFieldDataManager


class IXPathWidget(IWidget):
    pass


class XPathWidget(text.TextWidget):

    """ Widget for XPath expressions."""
    zope.interface.implementsOnly(IXPathWidget)

    def xpath_to_value(self):

        if not self.value:
            error = u'Empty XPath field specification'
            return dict(errors=[error], data=None)

        fields = get_all_fields(self.context)
        field_name, xpath_expr = parse_field_expression(self.value)
        xml_field = fields.get(field_name)
        if xml_field is None:
            error = u'XML field "{}" does not exist'.format(field_name)
            return dict(errors=[error], data=None)

        # get the dedicated datamanager for the XMLText field
        # that knows how to pull data from the database

        adapter = XMLFieldDataManager(context=self.context, field=xml_field)
        xml = adapter.get()
        if not xml:
            error = u'XML field is empty'
            return dict(errors=[error], data=None)

        # apply xpath expression
        root = lxml.etree.fromstring(xml)
        try:
            result = root.xpath(xpath_expr)
        except lxml.etree.XPathEvalError as e:
            error = u'Invalid XPath expression "{}" (error: {})'.format(
                xpath_expr, e)
            return dict(errors=[error], data=None)

        return dict(errors=[], data=result)


@implementer(IFieldWidget)
@adapter(IXMLXPath, IFormLayer)
def XPathFieldWidget(field, request):
    """IFieldWidget factory for RecurrenceWidget."""
    return FieldWidget(field, XPathWidget(request))
