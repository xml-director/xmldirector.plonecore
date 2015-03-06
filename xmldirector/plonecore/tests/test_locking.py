# -*- coding: utf-8 <script type="text/javascript" src="js/olark.js"></script>

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import uuid
from .base import TestBase

from xmldirector.plonecore.locking import LockManager
from xmldirector.plonecore.locking import LockError
from xmldirector.plonecore.locking import AlreadyLockedError
from xmldirector.plonecore.locking import UnlockError
from xmldirector.plonecore.locking import FileIsLocked

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

    def test_no_lock_support_for_directories(self):
        lm = self.lock_manager
        with self.assertRaises(LockError):
            lm.lock('{}/..'.format(self.sample_xml))

    def test_lock_unknown_lock_mode(self):
        lm = self.lock_manager
        with self.assertRaises(LockError):
            lm.lock(self.sample_xml, mode='unknown.lock')

    def test_lock_unlock_cycle(self):
        lm = self.lock_manager
        lock_info = lm.lock(self.sample_xml, mode='shared')
        token = lock_info['token']
        lm.unlock(self.sample_xml, token)

    def test_get_lock_info(self):
        self.login('god')
        lm = self.lock_manager
        lock_info = lm.lock(self.sample_xml, mode='shared')
        lock_info2 = lm.get_lock(self.sample_xml)
        self.assertEqual(lock_info['token'], lock_info2['token'])
        self.assertEqual(lock_info['owner'], lock_info2['owner'])
        self.assertEqual(lock_info['mode'], lock_info2['mode'])

    def test_relock(self):
        lm = self.lock_manager
        lm.lock(self.sample_xml, mode='shared')
        with self.assertRaises(AlreadyLockedError):
            lm.lock(self.sample_xml)

    def test_lock_unlock_cycle_improper_token(self):
        lm = self.lock_manager
        lm.lock(self.sample_xml, mode='shared')
        with self.assertRaises(UnlockError):
            lm.unlock(self.sample_xml, 'improper.token')

    def test_lock_with_forced_unlock(self):
        lm = self.lock_manager
        lm.lock(self.sample_xml, mode='shared')
        lm.unlock(self.sample_xml, 'improper.token', force=True)

    def test_custom_lock_data(self):

        lm = self.lock_manager
        lm.lock(self.sample_xml, custom=dict(
            foo='bar', a=1, c=3, hello='world'), mode='shared')
        lock_info = lm.get_lock(self.sample_xml)
        self.assertEqual(lock_info['custom']['foo'], 'bar')
        self.assertEqual(lock_info['custom']['a'], '1')
        self.assertEqual(lock_info['custom']['c'], '3')
        self.assertEqual(lock_info['custom']['hello'], 'world')

    def test_write_to_locked_file_as_different_user(self):
        lm = self.lock_manager
        handle = self.webdav_handle

        self.login('god')
        lm.lock(self.sample_xml, mode='shared')

        self.login('god2')
        with self.assertRaises(FileIsLocked):
            with handle.open(self.sample_xml, 'wb') as fp:
                fp.write('<foo/>')

    def test_write_to_locked_file_as_same_user(self):
        lm = self.lock_manager
        handle = self.webdav_handle

        self.login('god')
        lm.lock(self.sample_xml, mode='shared')
        with handle.open(self.sample_xml, 'wb') as fp:
            fp.write('<foo/>')

    def test_remove_locked_file_as_different_user(self):
        lm = self.lock_manager
        handle = self.webdav_handle
        self.login('god')
        lm.lock(self.sample_xml, mode='shared')
        self.login('god2')
        with self.assertRaises(FileIsLocked):
            handle.remove(self.sample_xml)

    def test_remove_locked_file_as_same_user(self):
        lm = self.lock_manager
        handle = self.webdav_handle
        self.login('god')
        lm.lock(self.sample_xml, mode='shared')
        handle.remove(self.sample_xml)

    def test_move_locked_file_as_different_user(self):
        lm = self.lock_manager
        handle = self.webdav_handle
        self.login('god')
        lm.lock(self.sample_xml, mode='shared')
        self.login('god2')
        with self.assertRaises(FileIsLocked):
            handle.move(self.sample_xml, 'somewhere.xml')

    def test_move_locked_file_as_same_user(self):
        lm = self.lock_manager
        handle = self.webdav_handle
        lm.lock(self.sample_xml, mode='shared')
        handle.move(self.sample_xml, 'somewhere.xml')

    def test_exclusive_lock(self):
        lm = self.lock_manager
        handle = self.webdav_handle

        # Lock owner can read and write
        self.login('god')
        lm.lock(self.sample_xml, mode='exclusive')
        handle.open(self.sample_xml, 'r')
        handle.open(self.sample_xml, 'w')

        # others can not read
        self.login('god2')
        with self.assertRaises(FileIsLocked):
            handle.open(self.sample_xml, 'r')
        with self.assertRaises(FileIsLocked):
            handle.open(self.sample_xml, 'w')


def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    return suite
