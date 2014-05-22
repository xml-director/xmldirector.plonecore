################################################################
# zopyx.existdb
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################

from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes.public import IntegerField, SelectionWidget, DisplayList, BooleanField, BooleanWidget, StringField
from Products.ATContentTypes.interface import IATImage


ScaleVocabulary= DisplayList((
     ('100', '100 %'),
     ('90', '90 %'),
     ('80', '80 %'),
     ('70', '70 %'),
     ('60', '60 %'),
     ('50', '50 %'),
     ('40', '40 %'),
     ('30', '30 %'),
     ('20', '20 %'),
     ('10', '10 %'),
))


CaptionPositionVocabulary = DisplayList((
     (u'top', u'Top'),
     (u'bottom', u'Bottom'),
))

class MyIntegerField(ExtensionField, IntegerField):
    """ integer field """

class MyBooleanField(ExtensionField, BooleanField):
    """ bool field """

class MyStringField(ExtensionField, StringField):
    """ string field """


class ImageExtender(object):
    """ add a dedicated (optional) field to ATImage for
        storing an "original" or Hires file e.g. an EPS
        or hi-res TIFF image.
    """

    adapts(IATImage)
    implements(ISchemaExtender)

    fields = [MyIntegerField('pdfScale',
                             default=100,
                             vocabulary=ScaleVocabulary,
                             widget=SelectionWidget(
                                label=u"Scale for PDF production",
                                label_msgid='label_scale_for_pdf',
                                i18n_domain='producepublish',
                                ),  
                             schemata='PDF',
                             ),  
              MyBooleanField('excludeFromImageEnumeration',
                             default=False,
                             widget=BooleanWidget(
                                label=u"Exclude from image enumeration",
                                label_msgid='label_exclude_from_image_enumeration',
                                i18n_domain='producepublish',
                                ),  
                             schemata='PDF',
                             ),  
              MyBooleanField('linkToFullScale',
                             default=False,
                             widget=BooleanWidget(
                                label=u'Create image link to full scale in HTML view',
                                label_msgid='label_create_link_to_full_scale',
                                i18n_domain='producepublish',
                                ),  
                             schemata='PDF',
                             ),  
              MyBooleanField('displayInline',
                             default=False,
                             widget=BooleanWidget(
                                label=u'Display image inline ',
                                label_msgid='label_display_image_inline',
                                i18n_domain='producepublish',
                                ),  
                             schemata='PDF',
                             ),  
              MyStringField('captionPosition',
                             default='bottom',
                             vocabulary=CaptionPositionVocabulary,
                             widget=SelectionWidget(
                                label=u'Caption position',
                                label_msgid='label_caption_position',
                                i18n_domain='producepublish',
                                format='select',
                                ),  
                             schemata='PDF',
                             ),  
            ] 


    def __init__(self, context):
        self.context = context

    def getFields(self):
        # extend only inside an authoring project
        try:
            self.context.getAuthoringProject()
            return self.fields
        except AttributeError:
            return ()

