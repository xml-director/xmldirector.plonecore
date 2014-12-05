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


def normalize_xml(xml):
    if not xml:
        u''
    if isinstance(xml, unicode):
        xml = xml.encode('utf-8')
    xml = xml.replace('\r\n', '\n')
    return xml


def xml_hash(xml):
    """ Get a stable hash from XML string """
    xml = normalize_xml(xml)
    if xml.startswith('<?xml'):
        xml = xml[xml.find('?>')+2:]
        xml = xml.lstrip('\n')
    return hashlib.sha256(xml).hexdigest()


################################################################
# XML Content
################################################################

class IXMLText(IField):
    """ Marker for XML fields """
    pass


class XMLText(Text):
    zope.interface.implements(IXMLText)

    def validate(self, value):
        """ Perform XML validation """
        if value:
            try:
                root = lxml.etree.fromstring(normalize_xml(value))
            except lxml.etree.XMLSyntaxError as e:
                raise zope.interface.Invalid(u'XML syntax error {}'.format(e))
        return super(XMLText, self).validate(value)

XMLTextFactory = FieldFactory(XMLText, _(u'label_xml_field', default=u'XML'))
XMLTextHandler = plone.supermodel.exportimport.BaseHandler(XMLText)

################################################################
# XML Binary Content
################################################################

class IXMLBinary(IField):
    """ Marker for XML fields """
    pass


class XMLBinary(NamedBlobFile):
    zope.interface.implements(IXMLBinary)

    def validate(self, value):
        """ Perform validation """
        return super(XMLBinary, self).validate(value)

XMLBinaryFactory = FieldFactory(XMLBinary, _(u'label_xml_binary_field', default=u'XMLBinary'))
XMLBinaryHandler = plone.supermodel.exportimport.BaseHandler(XMLBinary)


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


# Custom data manager
# for XML Content

class AttributeField(DataManager):
    """Attribute field."""
    zope.component.adapts(
        zope.interface.Interface, IXMLText)

    def __init__(self, context, field):
        self.context = context
        self.field = field

    @property
    def webdav_handle(self):

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
        context_id = getattr(self.context, '__xml_storage_id__', None)
        if not context_id:
            context_id = self.context.__xml_storage_id__ = uuid.uuid4()
        field_id = self.field.__name__
        return 'plone-data/{}/{}/{}.xml'.format(plone_uid, context_id, field_id)

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
#            if xml_hash(xml) != xml_sha256:    
#                raise ValueError('Hashes for {} differ'.format(storage_key))
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
            handle.makedir(dirname, True, True)
        value_utf8 = normalize_xml(value)
        value_sha256 = xml_hash(value_utf8)
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

class XMLBinaryDatamanager(DataManager):
    """Attribute field."""
    zope.component.adapts(
        zope.interface.Interface, IXMLBinary)

    def __init__(self, context, field):
        self.context = context
        self.field = field

    @property
    def webdav_handle(self):

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
        context_id = getattr(self.context, '__xml_storage_id__', None)
        if not context_id:
            context_id = self.context.__xml_storage_id__ = uuid.uuid4()
        field_id = self.field.__name__
        return 'plone-data/{}/{}/{}.bin'.format(plone_uid, context_id, field_id)

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
                    data = fp.read()
                    data_sha256 = fp_sha.read()
            
            blob = NamedBlobFile()
            blob.data = data
            blob.contentType = 'bin/bin'
            blob.filename= 'abc.bin'
            return blob

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
        print value
        if not value:
            return
        handle = self.webdav_handle
        storage_key = self.storage_key
        dirname = os.path.dirname(storage_key)
        if not handle.exists(dirname):
            handle.makedir(dirname, True, True)
        value_sha256 = hashlib.sha256(value.data).hexdigest()
        with handle.open(storage_key, 'wb') as fp:
            with handle.open(storage_key + '.sha256', 'wb') as fp_sha:
                fp.write(value.data)
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
