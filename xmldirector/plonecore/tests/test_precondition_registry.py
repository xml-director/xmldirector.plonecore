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


def view_handler2(webdav_handle, filename, view_name, request):
    return u'world hello'


def default_handler(webdav_handle, filename, view_name, request):
    return u'default handler'


class class_view_handler(object):

    def __call__(self, webdav_handle, filename, view_name, request):
        return 'i am a class view handler'


class PreconditionTests(unittest2.TestCase):

    def test_precondition_arguments(self):

        with self.assertRaises(TypeError):
            Precondition(suffixes='xxxx', view_names=['view'])

        with self.assertRaises(TypeError):
            Precondition(suffixes=['.a'], view_names='xxxx')

    def test_precondition(self):
        p = Precondition(
            suffixes=('.html',), view_names = ['htmlview'], view_handler=view_handler)
        self.assertEqual(p.can_handle('test.html', 'htmlview'), True)
        self.assertEqual(p.can_handle('test.html', 'xxxxxx'), False)
        self.assertEqual(p.can_handle('test.xxx', 'htmlview'), False)
        str(p)

    def test_precondition_handle_view(self):
        p = Precondition(
            suffixes=('html',), view_names = ['htmlview'], view_handler=view_handler)
        result = p.handle_view(webdav_handle=None,
                               filename='test.html',
                               view_name='view',
                               request=None)
        self.assertEqual(result, u'hello world')


class PreconditionRegistryTests(unittest2.TestCase):

    def setUp(self):
        self.registry = PreconditionRegistry()

    def test_registry(self):
        self.assertEqual(len(self.registry), 0)
        with self.assertRaises(ValueError):
            # nothing registered
            self.registry.dispatch(
                webdav_handle=None, filename='test.html', view_name='htmlview', request=None)

    def test_correct_entries(self):
        p = Precondition(
            suffixes=('.html',), view_names=['htmlview'], view_handler=view_handler)
        self.registry.register(p)
        p = Precondition(
            suffixes=('.xml',), view_names=['xmlview'], view_handler=view_handler2)
        self.registry.register(p)

        result = self.registry.dispatch(
            webdav_handle=None, filename='test.html', view_name='htmlview', request=None)
        self.assertEqual(result, u'hello world')

        result = self.registry.dispatch(
            webdav_handle=None, filename='test.xml', view_name='xmlview', request=None)
        self.assertEqual(result, u'world hello')

        with self.assertRaises(ValueError):
            self.registry.dispatch(
                webdav_handle=None, filename='test.xml', view_name='htmlview', request=None)

    def test_default_fallback(self):
        self.registry.set_default(Precondition(view_handler=default_handler))
        result = self.registry.dispatch(
            webdav_handle=None, filename='xxxxx', view_name='xxxxxx', request=None)
        self.assertEqual(result, u'default handler')

    def test_class_as_view_handler(self):
        self.registry.set_default(
            Precondition(view_handler=class_view_handler))
        result = self.registry.dispatch(
            webdav_handle=None, filename='xxxxx', view_name='xxxxxx', request=None)
        self.assertEqual(result, u'i am a class view handler')

    def test_register_improper_tyoe(self):
        with self.assertRaises(TypeError):
            self.registry.register(None)


def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PreconditionTests))
    suite.addTest(makeSuite(PreconditionRegistryTests))
    return suite
