# -*- coding: utf-8 -*-

################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

from base import TestBase
import plone.api


class BasicTests(TestBase):

    def testCreateTestFolder(self):
        assert self.portal.connector.portal_type == 'zopyx.existdb.connector'


def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    return suite
