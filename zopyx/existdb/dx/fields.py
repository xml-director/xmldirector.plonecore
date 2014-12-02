################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import hashlib
import plone.api
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



def normalize_xml(xml):
    if isinstance(xml, unicode):
        xml = xml.encode('utf-8')
    xml = xml.replace('\r\n', '\n')
    return xml


class IXMLField(IField):
    """ Marker for XML fields """
    pass


class XML(Text):
    zope.interface.implements(IXMLField)

    def validate(self, value):
        """ Perform XML validation """
        try:
            root = lxml.etree.fromstring(normalize_xml(value))
        except lxml.etree.XMLSyntaxError as e:
            raise zope.interface.Invalid(u'XML syntax error {}'.format(e))

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
    def webdav_handle(self):

        from fs.contrib.davfs import DAVFS
        from zope.component import getUtility
        from plone.registry.interfaces import IRegistry
        from zopyx.existdb.interfaces import IExistDBSettings

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IExistDBSettings)

        url = settings.existdb_url
        url = '{}/exist/webdav/db'.format(url)
        username = settings.existdb_username
        password = settings.existdb_password

        return DAVFS(url, credentials=dict(username=username,
                                           password=password))
    @property
    def storage_key(self):
        plone_uid = plone.api.portal.get().getId()
        context_uid = self.context.UID()
        field_id = self.field.__name__
        return '{}/{}-{}.xml'.format(plone_uid, context_uid, field_id)

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
        handle = self.webdav_handle
        storage_key = self.storage_key
        if handle.exists(storage_key):
            with handle.open(storage_key, 'rb') as fp:
                with handle.open(storage_key + '.sha256', 'rb') as fp_sha:
                    xml = fp.read()
                    xml_sha256 = fp_sha.read()
            if hashlib.sha256(xml).hexdigest() != xml_sha256:
                raise ValueError('Hashes for {} differ'.format(storage_key))
            return xml

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
        handle = self.webdav_handle
        storage_key = self.storage_key
        dirname = os.path.dirname(storage_key)
        if not handle.exists(dirname):
            handle.makedir(dirname, False, True)
        value_utf8 = normalize_xml(value)
        value_sha256 = hashlib.sha256(value_utf8).hexdigest()
        with handle.open(storage_key, 'wb') as fp:
            with handle.open(storage_key + '.sha256', 'wb') as fp_sha:
                fp.write(value_utf8)
                fp_sha.write(value_sha256)

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

