# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import hashlib
import plone.api

import zope.schema
import zope.interface
import zope.component
from zope.schema.interfaces import IField
from z3c.form.datamanager import AttributeField as AttributeDataManager
import plone.supermodel.exportimport
from plone.schemaeditor.fields import FieldFactory
from plone.namedfile import NamedFile
from plone.namedfile.field import NamedFile as NamedFileField

from xmldirector.plonecore.i18n import MessageFactory as _
from xmldirector.plonecore.interfaces import IWebdavHandle
from xmldirector.plonecore.dx import util


################################################################
# XML Binary Content
################################################################

class IXMLBinary(IField):

    """ Marker for XML fields """
    pass


class XMLBinary(NamedFileField):
    zope.interface.implements(IXMLBinary)


XMLBinaryFactory = FieldFactory(
    XMLBinary, _(u'label_xml_binary_field', default=u'XML (binary data)'))
XMLBinaryHandler = plone.supermodel.exportimport.BaseHandler(XMLBinary)


class XMLBinaryDataManager(AttributeDataManager):

    """Attribute field."""
    zope.component.adapts(
        zope.interface.Interface, IXMLBinary)

    suffix = '.bin'
    return_class = NamedFile

    @property
    def storage_key(self):
        context_id = util.get_storage_key(self.context)
        if not context_id:
            context_id = util.new_storage_key(self.context)
        field_id = self.field.__name__
        return '{}/{}{}'.format(util.get_storage_path(self.context), field_id, self.suffix)

    def get(self):
        """See z3c.form.interfaces.IDataManager"""

        handle = zope.component.getUtility(IWebdavHandle).webdav_handle()
        storage_key = self.storage_key
        if handle.exists(storage_key):
            with handle.open(storage_key, 'rb') as fp:
                with handle.open(storage_key + '.metadata.xml', 'rb') as fp_metadata:
                    data = fp.read()
                    metadata = util.xml_to_metadata(fp_metadata.read())

            if hashlib.sha256(data).hexdigest() != metadata['sha256']:
                raise ValueError(
                    'Invalid hash values for {}'.format(storage_key))

            return self.return_class(
                data,
                filename=metadata['filename'],
                contentType=str(metadata['contenttype']))

    def set(self, value):
        """See z3c.form.interfaces.IDataManager"""

        handle = zope.component.getUtility(IWebdavHandle).webdav_handle()
        storage_key = self.storage_key

        if not value:
            for name in (self.storage_key, self.storage_key + '.metadata.xml'):
                if handle.exists(name):
                    handle.remove(name)
            return

        dirname = os.path.dirname(storage_key)
        if not handle.exists(dirname):
            handle.makedir(dirname, True, True)
        metadata = dict(sha256=hashlib.sha256(value.data).hexdigest(),
                        filename=value.filename,
                        contenttype=value.contentType)
        with handle.open(storage_key, 'wb') as fp:
            with handle.open(storage_key + '.metadata.xml', 'wb') as fp_metadata:
                fp.write(value.data)
                fp_metadata.write(
                    util.metadata_to_xml(context=self.context, metadata=metadata))
