# -*- coding: utf-8 -*-

################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
from zipfile import ZipFile
from base import TestBase
from base import EXIST_DB_URL
import plone.api


class BasicTests(TestBase):

    def setUp(self):
        handle = self.portal.connector.webdav_handle()
        if handle.exists('_testing_'):
            handle.removedir('_testing_', False,  True)
        handle.makedir('_testing_')
        handle.makedir('_testing_/foo')
        with handle.open('_testing_/foo/index.html', 'wb') as fp:
            fp.write('<html/>')
        with handle.open('_testing_/foo/index.xml', 'wb') as fp:
            fp.write('<?xml version="1.0" ?>\n<hello>world</hello>')
        self.portal.connector.existdb_subpath = '_testing_'

    def tearDown(self):
        self.portal.connector.existdb_subpath = None
        handle = self.portal.connector.webdav_handle()
        if handle.exists('_testing_'):
            handle.removedir('_testing_', False,  True)

    def testCheckPortalType(self):
        assert self.portal.connector.portal_type == 'zopyx.existdb.connector'

    def testCheckWebdavHandle(self):
        handle = self.portal.connector.webdav_handle()
        self.assertEqual(handle.url, EXIST_DB_URL + '/exist/webdav/db/_testing_/')

    def testFileCheck(self):
        handle = self.portal.connector.webdav_handle()
        self.assertEqual(handle.exists('foo/index.html'), True)
        self.assertEqual(handle.exists('foo/index.xml'), True)
        self.assertEqual(handle.exists('foo/xxxx.html'), False)

    def testZipExport(self):
        self.login('god')
        view = self.portal.connector.restrictedTraverse('@@connector-zip-export')
        fn = view.zip_export(download=False)
        zf = ZipFile(fn, 'r')
        self.assertEqual('foo/index.html' in zf.namelist(), True)
        self.assertEqual('foo/index.xml' in zf.namelist(), True)
        zf.close()
        os.unlink(fn)

def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    return suite
