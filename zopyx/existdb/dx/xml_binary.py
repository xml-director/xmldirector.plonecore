################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import json
import os
import uuid
import hashlib
import plone.api
from fs.contrib.davfs import DAVFS

import zope.schema
import zope.interface
import zope.component
from zope.schema.interfaces import IField
from zope.component import getUtility
from z3c.form.datamanager import AttributeField as AttributeDataManager
import plone.supermodel.exportimport
from plone.registry.interfaces import IRegistry
from plone.schemaeditor.fields import FieldFactory
from plone.namedfile import NamedFile
from plone.namedfile.field import NamedFile as NamedFileField

from zopyx.existdb.i18n import MessageFactory as _
from zopyx.existdb.interfaces import IExistDBSettings
from zopyx.existdb.dx.xml_field import WebdavMixin


################################################################
# XML Binary Content
################################################################

class IXMLBinary(IField):
    """ Marker for XML fields """
    pass


class XMLBinary(NamedFileField):
    zope.interface.implements(IXMLBinary)


XMLBinaryFactory = FieldFactory(XMLBinary, _(u'label_xml_binary_field', default=u'XMLBinary'))
XMLBinaryHandler = plone.supermodel.exportimport.BaseHandler(XMLBinary)


class XMLBinaryDataManager(AttributeDataManager, WebdavMixin):
    """Attribute field."""
    zope.component.adapts(
        zope.interface.Interface, IXMLBinary)

    suffix = '.bin'
    return_class = NamedFile

    @property
    def storage_key(self):
        plone_uid = plone.api.portal.get().getId()
        context_id = getattr(self.context, '__xml_storage_id__', None)
        if not context_id:
            context_id = self.context.__xml_storage_id__ = uuid.uuid4()
        field_id = self.field.__name__
        return 'plone-data/{}/{}/{}{}'.format(plone_uid, context_id, field_id, self.suffix)

    def get(self):
        """See z3c.form.interfaces.IDataManager"""
        handle = self.webdav_handle
        storage_key = self.storage_key
        if handle.exists(storage_key):
            with handle.open(storage_key, 'rb') as fp:
                with handle.open(storage_key + '.metadata.json', 'rb') as fp_metadata:
                    data = fp.read()
                    metadata = json.load(fp_metadata)
            return self.return_class(
                data, 
                filename=metadata['filename'], 
                contentType=str(metadata['contenttype']))

    def set(self, value):
        """See z3c.form.interfaces.IDataManager"""

        handle = self.webdav_handle
        storage_key = self.storage_key

        if not value:
            for name in (self.storage_key, self.storage_key + '.metadata.json'):
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
            with handle.open(storage_key + '.metadata.json', 'wb') as fp_metadata:
                fp.write(value.data)
                fp_metadata.write(json.dumps(metadata))

