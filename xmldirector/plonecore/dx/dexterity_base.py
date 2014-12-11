################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


from xmldirector.plonecore.dx.xpath_field import get_all_fields

from xmldirector.plonecore.dx.xml_field import XMLText
from xmldirector.plonecore.dx.xml_field import XMLFieldDataManager
from xmldirector.plonecore.dx.xml_image import XMLImage
from xmldirector.plonecore.dx.xml_image import XMLImageDataManager
from xmldirector.plonecore.dx.xml_binary import XMLBinary
from xmldirector.plonecore.dx.xml_binary import XMLBinaryDataManager


_marker = object


def datamanager_for_field(context, fieldname, value=_marker):

    fields = get_all_fields(context)
    field = fields.get(fieldname)
    if not field:
        raise ValueError('No such field "{}"'.format(fieldname))

    if value is not _marker:
        field.validate(value)

    if isinstance(field, XMLText):
        dm_cls = XMLFieldDataManager
    elif isinstance(field, XMLBinary):
        dm_cls = XMLBinaryDataManager
    elif isinstance(field, XMLImage):
        dm_cls = XMLImageDataManager
    return dm_cls(context=context, field=field)


def xml_get(context, fieldname):

    dm = datamanager_for_field(context, fieldname)
    return dm.get()


def xml_set(context, fieldname, value):

    try:
        dm = datamanager_for_field(context, fieldname, value=value)
    except Exception as e:
        raise ValueError(e)
    return dm.set(value)


class Mixin(object):
    """ A mix-in class for Dexterity content XML fields in order
        to provide a consistent API for getting and setting content/data
        from application code.
    """

    def xml_get(self, fieldname):
        return xml_get(self, fieldname)

    def xml_set(self, fieldname, value):
        return xml_set(self, fieldname, value)
