# -*- coding: utf-8 -*-

################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import time
import requests
from requests.auth import HTTPBasicAuth

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from zExceptions import Forbidden

from zopyx.existdb.logger import LOG
from zopyx.existdb.interfaces import IExistDBSettings


class ExistDBError(Exception):
    pass


def timeit(method):
    """ A method timing decorator """

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        LOG.info('{:s}({:s}, {:s}) {:2.3f} sec'.format(method.__name__, args, kw, te-ts))
        return result
    return timed


class API(BrowserView):

    @timeit
    def generic_query(self, script_path='scripts/all-documents', output_format='json', **kw):
        """ Public eXist-db query API """

        if not self.context.api_enabled:
            raise Forbidden('API not enabled')

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IExistDBSettings)
        url = '{}/exist/restxq/{}.{}'.format(settings.existdb_url, script_path, output_format)
        username = settings.existdb_username
        password = settings.existdb_password
        result = requests.get(url, auth=HTTPBasicAuth(username, password), params=kw)
        if result.status_code != 200:
            raise ExistDBError('eXist-db return an response with HTTP code {} for {}'.format(result.status_code, url))
        return result.json()
