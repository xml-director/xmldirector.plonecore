# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import fs.errors
import zope.interface
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from xmldirector.plonecore.interfaces import IWebdavSettings
from xmldirector.plonecore.interfaces import IWebdavHandle
from xmldirector.plonecore.fswrapper import get_fs_wrapper


class WebdavHandle(object):

    zope.interface.implements(IWebdavHandle)

    def webdav_handle(self):
        """ Return WebDAV handle """

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IWebdavSettings)

        root_url = settings.webdav_url
        username = settings.webdav_username
        password = settings.webdav_password or ''

        if settings.webdav_dexterity_subpath:
            url = '{}/{}'.format(root_url, settings.webdav_dexterity_subpath)
        else:
            url = root_url
        try:
            return get_fs_wrapper(url, credentials=dict(username=username,
                                                        password=password))
        except fs.errors.ResourceNotFoundError:
            root_handle = get_fs_wrapper(root_url, credentials=dict(username=username,
                                                                    password=password))
            root_handle.makedir(settings.webdav_dexterity_subpath, True, True)
            return get_fs_wrapper(url, credentials=dict(username=username,
                                                        password=password))


WebdavHandleUtility = WebdavHandle()
