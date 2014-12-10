################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import json
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

from xmldirector.plonecore.i18n import MessageFactory as _
from xmldirector.plonecore.interfaces import IWebdavHandle
from xmldirector.plonecore.dx import util


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
        xml = xml[xml.find('?>') + 2:]
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


XMLTextFactory = FieldFactory(
    XMLText, _(u'label_xml_field', default=u'XML (Text)'))
XMLTextHandler = plone.supermodel.exportimport.BaseHandler(XMLText)


class XMLFieldDataManager(z3c.form.datamanager.AttributeField):

    """A dedicated manager for XMLText field."""
    zope.component.adapts(
        zope.interface.Interface, IXMLText)

    def __init__(self, context, field):
        self.context = context
        self.field = field

    @property
    def storage_key(self):

        context_id = util.get_storage_key(self.context)
        if not context_id:
            context_id = util.new_storage_key(self.context)
        field_id = self.field.__name__
        return '{}/{}.xml'.format(util.get_storage_path(self.context), field_id)

    def get(self):
        """See z3c.form.interfaces.IDataManager"""

        handle = zope.component.getUtility(IWebdavHandle).webdav_handle()
        storage_key = self.storage_key
        if handle.exists(storage_key):
            with handle.open(storage_key, 'rb') as fp:
                with handle.open(storage_key + '.metadata.json', 'rb') as fp_metadata:
                    xml = fp.read()
                    metadata = json.loads(fp_metadata.read())
            if xml_hash(xml) != metadata['sha256']:
                raise ValueError('Hashes for {} differ'.format(storage_key))
            return xml

    def set(self, value):
        """See z3c.form.interfaces.IDataManager"""

        handle = zope.component.getUtility(IWebdavHandle).webdav_handle()
        storage_key = self.storage_key
        dirname = os.path.dirname(storage_key)
        if not handle.exists(dirname):
            handle.makedir(dirname, True, True)
        value_utf8 = normalize_xml(value)
        value_sha256 = xml_hash(value_utf8)
        with handle.open(storage_key, 'wb') as fp:
            with handle.open(storage_key + '.metadata.json', 'wb') as fp_metadata:
                fp.write(value_utf8)
                metadata = dict(sha256=value_sha256)
                fp_metadata.write(json.dumps(metadata))
