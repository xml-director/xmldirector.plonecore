################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import lxml.etree
from zope.schema import Text
from zopyx.existdb.i18n import MessageFactory as _

from plone.schemaeditor.interfaces import IFieldFactory
from plone.schemaeditor.fields import FieldFactory
import plone.supermodel.exportimport


class XML(Text):

    def validate(self, value):

        try:
            root = lxml.etree.fromstring(value)
        except lxml.etree.XMLSyntaxError as e:
            raise ValueError(u'XML syntax error {}'.format(e))


XMLFactory = FieldFactory(XML, _(u'label_xml_field', default=u'XML'))
XMLHandler = plone.supermodel.exportimport.BaseHandler(XML)
