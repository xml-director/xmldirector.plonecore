# -*- coding: utf-8 -*-

################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import uuid
import plone.api
from zopyx.existdb.dx import webdav


def removal_handler(obj, event):
    """ Remove related XML content if a Dexterity content object
        is being deleted.
    """

    try:
        storage_key = event.object.__xml_storage_id__
    except AttributeError:
        return

    handle = webdav.webdav_handle()
    plone_uid = plone.api.portal.get().getId()
    storage_dir = '{}/{}/{}'.format(plone_uid, event.object.__xml_storage_id__[-4:], event.object.__xml_storage_id__)
    handle.removedir(storage_dir, False, True)


def copied_handler(obj, event):
    """ Copy XML resources to new object """

    # original and copied Dexterity object
    copied = event.object
    original = event.original

    # Is this Dexterity content object related to XML resources?
    try:
        copied.__xml_storage_id__
    except AttributeError:
        return

    # create a new storage id 
    if original.__xml_storage_id__ == copied.__xml_storage_id__:
        copied.__xml_storage_id__ = str(uuid.uuid4())

        # an copy over XML content from original content object
        handle = webdav.webdav_handle()
        plone_uid = plone.api.portal.get().getId()
        storage_dir_original = '{}/{}/{}'.format(plone_uid, original.__xml_storage_id__[-4:], original.__xml_storage_id__)
        storage_dir_copied = '{}/{}/{}'.format(plone_uid, copied.__xml_storage_id__[-4:], copied.__xml_storage_id__)
        storage_dir_copied_parent = '{}/{}'.format(plone_uid, copied.__xml_storage_id__[-4:])
        handle.makedir(storage_dir_copied_parent, True, True)
        handle.copydir(storage_dir_original, storage_dir_copied)
