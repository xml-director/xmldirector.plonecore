# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import unittest2
from xmldirector.plonecore.xslt_registry import XSLTRegistry

cwd = os.path.dirname(__file__)


class BasicTests(unittest2.TestCase):

    def setUp(self):
        self.xslt_registry = XSLTRegistry()
        self.xslt_registry.xslt_registry.clear()

    def _register_one(self):
        self.xslt_registry.register_stylesheet(
            'demo', 'play.xsl', os.path.join(cwd, 'play.xsl'))

    def test_register(self):
        self._register_one()

    def test_register_twice(self):
        self._register_one()
        with self.assertRaises(ValueError):
            self._register_one()

    def test_registery_get_existing_xslt(self):
        self._register_one()
        self.xslt_registry.get_stylesheet('demo', 'play.xsl')

    def test_registery_get_nonexisting_xslt(self):
        self._register_one()
        with self.assertRaises(ValueError):
            self.xslt_registry.get_stylesheet('xxx', 'xxx')


def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    return suite
