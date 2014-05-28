from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides, implements
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.autoform import directives as form
from z3c.form.browser.select import SelectWidget

from zopyx.existdb import MessageFactory as _


def context_property(name):
    def getter(self):
        return getattr(self.context, name)
    def setter(self, value):
        setattr(self.context, name, value)
    def deleter(self):
        delattr(self.context, name)
    return property(getter, setter, deleter)


language_vocab = SimpleVocabulary([
    SimpleTerm(value=u'de', title=_(u'German')),
    SimpleTerm(value=u'en', title=_(u'English')),
])

area_vocab = SimpleVocabulary([
    SimpleTerm(value=u'onkopedia', title=_(u'Onkopedia')),
    SimpleTerm(value=u'onkopedia-p', title=_(u'Onkopedia-P')),
    SimpleTerm(value=u'my-onkopedia', title=_(u'My Onkopedia')),
    SimpleTerm(value=u'knowledge-database', title=_(u'Knowledge database')),
])

state_vocab = SimpleVocabulary([
    SimpleTerm(value=u'draft', title=_(u'Draft')),
    SimpleTerm(value=u'current', title=_(u'Current')),
    SimpleTerm(value=u'archived', title=_(u'Archived')),
])

id_vocab = SimpleVocabulary([
    SimpleTerm(value=None, title=_(u'Nothing')),
    SimpleTerm(value=u'a', title=_(u'a')),
    SimpleTerm(value=u'b', title=_(u'b')),
    SimpleTerm(value=u'c', title=_(u'c')),
])


class IGuideline(model.Schema):
    """ Interface for Guideline behavior """
    
    model.fieldset(
        'fieldset_guideline',
        label=_(u'Guideline'),
        fields=['gl_language', 'gl_state', 'gl_area', 'gl_id', 'gl_archive_id']
    )
    gl_language = schema.Choice(
        title=_(u'Guideline language'),
        description=_(u"Language of guideline"),
        required=True,
        default=u'de',
        vocabulary=language_vocab
    )

    gl_state = schema.Choice(
        title=_(u'Guideline workflow state'),
        description=_(u"State of guideline"),
        required=True,
        default=u'draft',
        vocabulary=state_vocab
    )
#    
    gl_area = schema.Choice(
        title=_(u'Guideline area'),
        description=_(u"Content area for guideline"),
        required=True,
        default=u'onkopedia',
        vocabulary=area_vocab
    )
#
    gl_id = schema.Choice(
        title=_(u'Internal id'),
        description=_(u'Internal id representing the clinical picture'),
        required=True,
        default=None,
        vocabulary=id_vocab
    )

    gl_archive_id = schema.TextLine(
        title=_(u'ID in archive'),
        description=_(u'ID in archive'),
        required=False,
        default=u'',
    )

alsoProvides(IGuideline, IFormFieldProvider)


class Guideline(object):
    """ Adapter for Guideline """
    implements(IGuideline)
    adapts(IDexterityContent)

    def __init__(self,context):
        self.context = context

    gl_language = context_property('gl_language')
    gl_state = context_property('gl_state')
    gl_area = context_property('gl_area')
    gl_id = context_property('gl_id')
    gl_archive_id = context_property('gl_archive_id')

