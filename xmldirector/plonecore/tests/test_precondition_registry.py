# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import unittest2
from xmldirector.plonecore.browser.view_registry import Precondition
from xmldirector.plonecore.browser.view_registry import PreconditionRegistry


cwd = os.path.dirname(__file__)


def view_handler(webdav_handle, filename, view_name, request):
    return u'hello world'


class PreconditionRegistryTests(unittest2.TestCase):

    def test_precondition_arguments(self):

        with self.assertRaises(TypeError):
            Precondition(suffixes='xxxx', view_names=['view'])

        with self.assertRaises(TypeError):
            Precondition(suffixes=['.a'], view_names='xxxx')

    def test_precondition(self):
        p = Precondition(suffixes=('.html',), view_names = ['htmlview'], view_handler=view_handler)
        self.assertEqual(p.can_handle('test.html', 'htmlview'), True)
        self.assertEqual(p.can_handle('test.html', 'xxxxxx'), False)
        self.assertEqual(p.can_handle('test.xxx', 'htmlview'), False)

    def test_precondition_handle_view(self):
        p = Precondition(suffixes=('.html',), view_names = ['htmlview'], view_handler=view_handler)
        result = p.handle_view(webdav_handle=None,
                filename='test.html',
                view_name='view',
                request=None)
        self.assertEqual(result, u'hello world')


def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PreconditionRegistryTests))
    return suite
