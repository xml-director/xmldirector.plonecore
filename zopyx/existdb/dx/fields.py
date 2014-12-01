################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import lxml.etree
from zopyx.existdb.i18n import MessageFactory as _

import plone.supermodel.exportimport
from plone.schemaeditor.fields import FieldFactory
from plone.schemaeditor.interfaces import IFieldFactory

import zope.schema
import zope.interface
import zope.component
from zope.schema import Text
from zope.schema.interfaces import IField
from zope.security.interfaces import ForbiddenAttribute
from zope.security.checker import canAccess, canWrite, Proxy
from z3c.form import interfaces
from z3c.form.datamanager import DataManager


class IXMLField(IField):
    """ Marker for XML fields """
    pass


class XML(Text):
    zope.interface.implements(IXMLField)

    def validate(self, value):
        """ Perform XML validation """
        try:
            root = lxml.etree.fromstring(value)
        except lxml.etree.XMLSyntaxError as e:
            raise ValueError(u'XML syntax error {}'.format(e))
        return super(XML, self).validate(value)


XMLFactory = FieldFactory(XML, _(u'label_xml_field', default=u'XML'))
XMLHandler = plone.supermodel.exportimport.BaseHandler(XML)

# Custom data manager

class AttributeField(DataManager):
    """Attribute field."""
    zope.component.adapts(
        zope.interface.Interface, IXMLField)

    def __init__(self, context, field):
        self.context = context
        self.field = field

    @property
    def adapted_context(self):
        # get the right adapter or context
        context = self.context
        # NOTE: zope.schema fields defined in inherited interfaces will point
        # to the inherited interface. This could end in adapting the wrong item.
        # This is very bad because the widget field offers an explicit interface
        # argument which doesn't get used in Widget setup during IDataManager
        # lookup. We should find a concept which allows to adapt the
        # IDataManager use the widget field interface instead of the zope.schema
        # field.interface, ri
        if self.field.interface is not None:
            context = self.field.interface(context)
        return context

    def get(self):
        """See z3c.form.interfaces.IDataManager"""
        return getattr(self.adapted_context, self.field.__name__)

    def query(self, default=interfaces.NO_VALUE):
        """See z3c.form.interfaces.IDataManager"""
        try:
            return self.get()
        except ForbiddenAttribute as e:
            raise e
        except AttributeError:
            return default

    def set(self, value):
        """See z3c.form.interfaces.IDataManager"""
        if self.field.readonly:
            raise TypeError("Can't set values on read-only fields "
                            "(name=%s, class=%s.%s)"
                            % (self.field.__name__,
                               self.context.__class__.__module__,
                               self.context.__class__.__name__))
        # get the right adapter or context
        setattr(self.adapted_context, self.field.__name__, value)

    def canAccess(self):
        """See z3c.form.interfaces.IDataManager"""
        context = self.adapted_context
        if isinstance(context, Proxy):
            return canAccess(context, self.field.__name__)
        return True

    def canWrite(self):
        """See z3c.form.interfaces.IDataManager"""
        context = self.adapted_context
        if isinstance(context, Proxy):
            return canWrite(context, self.field.__name__)
        return True

