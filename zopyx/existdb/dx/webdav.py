# -*- coding: utf8 -*-

################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import fs.errors
from fs.contrib.davfs import DAVFS
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from zopyx.existdb.interfaces import IExistDBSettings


def webdav_handle():
    """ Return WebDAV handle """

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
