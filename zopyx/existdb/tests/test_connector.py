# -*- coding: utf-8 -*-

################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

from base import TestBase
import plone.api


class BasicTests(TestBase):

    def testCheckPortalType(self):
        assert self.portal.connector.portal_type == 'zopyx.existdb.connector'

    def testCheckWebdavHandle(self):
        handle = self.portal.connector.webdav_handle()
        assert handle.url == 'http://localhost:6080/exist/webdav/db/'


def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    return suite
