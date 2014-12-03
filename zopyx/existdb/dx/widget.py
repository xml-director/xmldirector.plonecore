################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


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


class IXPathWidget(zope.interface.Interface):
    pass


class XPathWidget(text.TextWidget):
    """Input type password widget implementation."""
    zope.interface.implementsOnly(IXPathWidget)

class XPathDataConverter(converter.FieldDataConverter):
    """A data converter using the field's ``fromUnicode()`` method."""
    zope.component.adapts(
        zope.schema.interfaces.IFromUnicode, 
        IXPathWidget)
    zope.interface.implements(IDataConverter)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        # check for empty form input
        import pdb; pdb.set_trace() 
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
