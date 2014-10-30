# -*- coding: utf-8 -*-

################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

from base import TestBase
from base import EXIST_DB_URL
import plone.api


class BasicTests(TestBase):

    def testCheckPortalType(self):
        assert self.portal.connector.portal_type == 'zopyx.existdb.connector'

    def testCheckWebdavHandle(self):
        handle = self.portal.connector.webdav_handle()
        self.assertEqual(handle.url, EXIST_DB_URL + '/exist/webdav/db/')

    def testMkdirRemovedir(self):
        handle = self.portal.connector.webdav_handle()
        handle.makedir('_testing_')
        handle.removedir('_testing_')

def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    return suite
