# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import fs.errors
import zope.interface
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from xmldirector.plonecore.interfaces import IConnectorSettings
from xmldirector.plonecore.interfaces import IConnectorHandle
from xmldirector.plonecore.fswrapper import get_fs_wrapper


class ConnectorHandle(object):

    zope.interface.implements(IConnectorHandle)

    def get_handle(self):
        """ Return Connector handle """

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IConnectorSettings)

        root_url = settings.connector_url
        username = settings.connector_username
        password = settings.connector_password or ''

        if settings.connector_dexterity_subpath:
            url = '{}/{}'.format(root_url,
                                 settings.connector_dexterity_subpath)
        else:
            url = root_url
        try:
            return get_fs_wrapper(url, credentials=dict(username=username,
                                                        password=password))
        except fs.errors.ResourceNotFoundError:
            root_handle = get_fs_wrapper(root_url, credentials=dict(username=username,
                                                                    password=password))
            root_handle.makedir(
                settings.connector_dexterity_subpath, True, True)
            return get_fs_wrapper(url, credentials=dict(username=username,
                                                        password=password))


ConnectorHandleUtility = ConnectorHandle()
