
################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import uuid
import plone.api
from Acquisition import aq_base, aq_inner


STORAGE_KEY = '__xml_storage_id__'


def is_xml_content(context):
    """ Check if the ``context`` object is an XML content type """

    base = aq_base(aq_inner(context))
    try:
        getattr(base, STORAGE_KEY)
        return True
    except AttributeError:
        return False


def new_storage_key(context):
    """ Set a new UUID on the given ``context`` object """

    key = str(uuid.uuid4())
    setattr(context, STORAGE_KEY, key)
    return key


def get_storage_key(context):
    """ Return the storage key of the given ``context`` object """

    base = aq_base(aq_inner(context))
    try:
        return getattr(base, STORAGE_KEY)
    except AttributeError:
        return None


def get_storage_path(context):
    """ Storage path of the given ``context`` object with the database """

    storage_key = get_storage_key(context)
    plone_uid = plone.api.portal.get().getId()
    return '{}/{}/{}'.format(plone_uid, storage_key[-4:], storage_key)


def get_storage_path_parent(context):
    """ Storage path of the parent container of the given ``context`` object with the database """

    storage_key = get_storage_key(context)
    plone_uid = plone.api.portal.get().getId()
    return '{}/{}'.format(plone_uid, storage_key[-4:])
