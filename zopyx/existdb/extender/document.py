################################################################
# zopyx.existdb
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################

from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes.public import BooleanField, BooleanWidget
from Products.ATContentTypes.interface import IATDocument

class MyBooleanField(ExtensionField, BooleanField):
    """ boolean field """


class DocumentExtender(object):
    """ PDF properties for ATDocument-ish types """

    adapts(IATDocument)
    implements(ISchemaExtender)

    fields = [MyBooleanField('pdfShowTitle',
                             default=True,
                             widget=BooleanWidget(
                                label="Show document title in PDF",
                                label_msgid='label_show_document_title_in_pdf',
                                i18n_domain='plone',
                                ),  
                             schemata='PDF',
                             ),  
            ] 


    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

