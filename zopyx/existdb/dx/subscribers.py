# -*- coding: utf-8 -*-

################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import uuid
import plone.api
import fs.errors
from fs.contrib.davfs import DAVFS
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from zopyx.existdb.interfaces import IExistDBSettings


def webdav_handle():

    registry = getUtility(IRegistry)
    settings = registry.forInterface(IExistDBSettings)

    root_url = settings.existdb_url
    username = settings.existdb_username
    password = settings.existdb_password
    if settings.existdb_dexterity_subpath:
        url = '{}/{}'.format(root_url, settings.existdb_dexterity_subpath)
    else:
        url = root_url
    try:
        return DAVFS(url, credentials=dict(username=username,
                                           password=password))
    except fs.errors.ResourceNotFoundError:
        root_handle = DAVFS(root_url, credentials=dict(username=username,
                                                       password=password))
        root_handle.makedir(settings.existdb_dexterity_subpath, True, True)
        return DAVFS(url, credentials=dict(username=username,
                                           password=password))


def removal_handler(obj, event):

    try:
        storage_key = event.object.__xml_storage_id__
    except AttributeError:
        return

    handle = webdav_handle()
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

        handle = webdav_handle()
        plone_uid = plone.api.portal.get().getId()
        storage_dir_old = '{}/{}'.format(plone_uid, old.__xml_storage_id__)
        storage_dir_new = '{}/{}'.format(plone_uid, current.__xml_storage_id__)
        handle.copydir(storage_dir_old, storage_dir_new)
