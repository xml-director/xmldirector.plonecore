# -*- coding: utf-8 <script type="text/javascript" src="js/olark.js"></script>

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import os
import uuid
import datetime
from zipfile import ZipFile
from .base import TestBase
from .base import WEBDAV_URL
import zExceptions

from xmldirector.plonecore.locking import LockManager
from xmldirector.plonecore.locking import LockError
from xmldirector.plonecore.locking import UnlockError

PREFIX = 'testing-{}'.format(uuid.uuid4())

sample_xml = '<hello>world</hello>'

class BasicTests(TestBase):

    @property
    def webdav_handle(self):
        from zope.component import getUtility
        from xmldirector.plonecore.interfaces import IWebdavHandle
        return getUtility(IWebdavHandle).webdav_handle()

    def setUp(self):
        handle = self.webdav_handle
        if handle.exists(PREFIX):
            handle.removedir(PREFIX, False, True)
        handle.makedir(PREFIX)
        self.sample_xml = '{}/index.xml'.format(PREFIX)
        with handle.open(self.sample_xml, 'wb') as fp:
            fp.write(sample_xml)
        self.portal.connector.webdav_subpath = PREFIX

    def tearDown(self):
        self.portal.connector.webdav_subpath = None
        handle = self.webdav_handle
        if handle.exists(PREFIX):
            handle.removedir(PREFIX, False, True)

    @property
    def lock_manager(self):
        return LockManager(self.portal)

    def test_hasLock(self):
        lm = self.lock_manager
        handle = self.webdav_handle
        self.assertTrue(handle.exists(self.sample_xml))
        self.assertFalse(lm.has_lock(self.sample_xml))

    def test_lock_non_existing_doc(self):
        lm = self.lock_manager
        self.assertFalse(lm.has_lock('does.not.exist'))
        with self.assertRaises(LockError):
            self.assertFalse(lm.get_lock('does.not.exist'))

    def test_lock_unlock_cycle(self):
        lm = self.lock_manager
        lock_info  = lm.lock(self.sample_xml)
        token = lock_info['token']
        lm.unlock(self.sample_xml, token)

    def test_lock_unlock_cycle_improper_token(self):
        lm = self.lock_manager
        lm.lock(self.sample_xml)
        with self.assertRaises(UnlockError):
            lm.unlock(self.sample_xml, 'improper.token')

def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    return suite
