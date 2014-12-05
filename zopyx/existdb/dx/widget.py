################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

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

#class IXPathWidget(zope.interface.Interface):
class IXPathWidget(IWidget):
    pass


class XPathWidget(text.TextWidget):
    """ Widget for XPath expressions."""
    zope.interface.implementsOnly(IXPathWidget)

    def xpath_to_value(self):

        from plone.dexterity.interfaces import IDexterityFTI
        from plone.behavior.interfaces import IBehaviorAssignable
         
        schema = zope.component.getUtility(
            IDexterityFTI, name=self.context.portal_type).lookupSchema()
        fields = dict((fieldname, schema[fieldname]) for fieldname in schema)

        assignable = IBehaviorAssignable(self.context)
        for behavior in assignable.enumerateBehaviors():
            behavior_schema = behavior.interface
            fields.update((name, behavior_schema[name]) for name in behavior_schema)

        print self.value
        parts = self.value.split(',', 1)
        fieldname = parts[0].split('=')[1]
        xpath_expr = parts[1].split('=')[1]
        print fieldname
        print xpath_expr
        xml_field = fields.get(fieldname)
        if not xml_field: 
            raise ValueError('No such field "{}"'.format(fieldname))

        import pdb; pdb.set_trace()                         

        from zopyx.existdb.dx.fields import AttributeField
        adapter = AttributeField(context=self.context, field=xml_field)
        xml = adapter.get()
        root = lxml.etree.fromstring(xml)
        result = root.xpath(xpath_expr)
        return result


class XPathDataConverter(converter.FieldDataConverter):
    """A data converter using the field's ``fromUnicode()`` method."""
    zope.component.adapts(
        zope.schema.interfaces.IFromUnicode, 
        IXPathWidget)
    zope.interface.implements(IDataConverter)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        # check for empty form input
        confirm = self.widget.request.get(self.widget.name + '.confirm', None)
        if value == u'' and confirm == u'' and self.field.required == False:
            # if there is a empty value, we return the field value if widget 
            # was set to required = False by the PasswordRequiredValue adapter
            return self.field.query(self.widget.context)
        return self.field.fromUnicode(value)

from z3c.form.widget import FieldWidget
from zopyx.existdb.dx.fields import IXMLXPath

@implementer(IFieldWidget)
@adapter(IXMLXPath, IFormLayer)
def XPathFieldWidget(field, request):
    """IFieldWidget factory for RecurrenceWidget."""
    return FieldWidget(field, XPathWidget(request))
