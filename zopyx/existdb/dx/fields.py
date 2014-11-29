################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


from zope.schema import Text
from zopyx.existdb.i18n import MessageFactory as _

from plone.schemaeditor.interfaces import IFieldFactory
from plone.schemaeditor.fields import FieldFactory


class XML(Text):
    pass


XMLFactory = FieldFactory(XML, _(u'label_xml_field', default=u'XML'))

