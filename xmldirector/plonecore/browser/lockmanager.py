# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


from zope.component import getUtility

from Products.Five.browser import BrowserView
from xmldirector.plonecore.interfaces import IWebdavHandle
from xmldirector.plonecore.browser.api import API
from xmldirector.plonecore.browser.api import APIError
from xmldirector.plonecore.logger import LOG


class LockManager(BrowserView):

    def entries(self):

        release_uri = self.request.get('release')
        if release_uri:
            handle = getUtility(IWebdavHandle).webdav_handle()
            release_uri = release_uri.lstrip('/db')
            if handle.exists(release_uri):
                handle.remove(release_uri)

        api_view = API(context=None, request=self.request)
        try:
            results = api_view.generic_query(
                'all-locks', deserialize_json=True)
        except APIError as e:
            msg = u'Unable to retrieve locks ({})'.format(e)
            LOG.error(msg, exc_info=False)
            return dict(error=msg, rows=())
        if results:
            return dict(error=None, rows=results['lock'])
        return dict(error=None, rows=())
