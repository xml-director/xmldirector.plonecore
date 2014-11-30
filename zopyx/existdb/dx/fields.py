################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import lxml.etree
from zope.schema import Text
from zopyx.existdb.i18n import MessageFactory as _

import plone.supermodel.exportimport
from plone.schemaeditor.fields import FieldFactory
from plone.schemaeditor.interfaces import IFieldFactory


class XML(Text):

    def get(self, obj):
        print obj
        return super(XML, self).get(obj)


    def set(self, obj, value):
        print obj, value
        return super(XML, self).set(obj, value)

    def validate(self, value):
        """ Perform XML validation """
        try:
            root = lxml.etree.fromstring(value)
        except lxml.etree.XMLSyntaxError as e:
            raise ValueError(u'XML syntax error {}'.format(e))
        return super(XML, self).validate(value)


XMLFactory = FieldFactory(XML, _(u'label_xml_field', default=u'XML'))
XMLHandler = plone.supermodel.exportimport.BaseHandler(XML)
