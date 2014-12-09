################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import uuid
import hashlib
import plone.api
import lxml.etree

import zope.schema
import zope.interface
import zope.component
from zope.schema import Text
from zope.schema.interfaces import IField
import z3c.form.datamanager
import plone.supermodel.exportimport
from plone.schemaeditor.fields import FieldFactory

from zopyx.existdb.i18n import MessageFactory as _
from zopyx.existdb.interfaces import IExistDBSettings
from zopyx.existdb.dx import webdav


def normalize_xml(xml):
    """ Normalize XML to utf8 encoded string
        with normalized line-endings.
    """
    if not xml:
        return u''
    if isinstance(xml, unicode):
        xml = xml.encode('utf-8')
    xml = xml.replace('\r\n', '\n')
    return xml


def xml_hash(xml):
    """ Get a stable SHA256 hash from XML string """
    xml = normalize_xml(xml)
    # remove XML preamble
    if xml.startswith('<?xml'):
        xml = xml[xml.find('?>')+2:]
        xml = xml.lstrip('\n')
    return hashlib.sha256(xml).hexdigest()


################################################################
# XML Content
################################################################

class IXMLText(IField):
    """ Marker for XML fields """


class XMLText(Text):
    zope.interface.implements(IXMLText)

    def validate(self, value):
        """ Perform XML validation """
        if value:
            try:
                lxml.etree.fromstring(normalize_xml(value))
            except lxml.etree.XMLSyntaxError as e:
                raise zope.interface.Invalid(u'XML syntax error {}'.format(e))
        return super(XMLText, self).validate(value)


XMLTextFactory = FieldFactory(XMLText, _(u'label_xml_field', default=u'XML (Text)'))
XMLTextHandler = plone.supermodel.exportimport.BaseHandler(XMLText)


class WebdavMixin(object):

    @property
    def webdav_handle(self):
        return webdav.webdav_handle()


class XMLFieldDataManager(z3c.form.datamanager.AttributeField, WebdavMixin):
    """A dedicated manager for XMLText field."""
    zope.component.adapts(
        zope.interface.Interface, IXMLText)

    def __init__(self, context, field):
        self.context = context
        self.field = field

    @property
    def storage_key(self):
        plone_uid = plone.api.portal.get().getId()
        context_id = getattr(self.context, '__xml_storage_id__', None)
        if not context_id:
            context_id = self.context.__xml_storage_id__ = str(uuid.uuid4())
        field_id = self.field.__name__
        return '{}/{}/{}/{}.xml'.format(plone_uid, context_id[-4:], context_id, field_id)

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

