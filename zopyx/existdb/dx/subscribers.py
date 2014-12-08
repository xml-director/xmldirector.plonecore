# -*- coding: utf-8 -*-

################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import uuid
import plone.api
from zopyx.existdb.dx import webdav


def removal_handler(obj, event):

    try:
        storage_key = event.object.__xml_storage_id__
    except AttributeError:
        return

    handle = webdav.webdav_handle()
    plone_uid = plone.api.portal.get().getId()
    storage_dir = '{}/{}'.format(plone_uid, event.object.__xml_storage_id__)
    handle.removedir(storage_dir, False, True)
    return


def copied_handler(obj, event):

        current = event.object
        old = event.original
        
        try:
            old.__xml_storage_id__
        except AttributeError:
            return

        if str(current.__xml_storage_id__) == str(old.__xml_storage_id__):
            current.__xml_storage_id__ = uuid.uuid4()

        handle = webdav.webdav_handle()
        plone_uid = plone.api.portal.get().getId()
        storage_dir_old = '{}/{}'.format(plone_uid, old.__xml_storage_id__)
        storage_dir_new = '{}/{}'.format(plone_uid, current.__xml_storage_id__)
        handle.copydir(storage_dir_old, storage_dir_new)
