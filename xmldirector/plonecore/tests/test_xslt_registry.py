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

    def test_register_invalid_xml_stylesheet(self):
        with self.assertRaises(ValueError):
            self.xslt_registry.register_stylesheet(
                'demo', 'play.xsl', os.path.join(cwd, 'play-invalid-xml.xsl'))

    def test_register_invalid_xslt_stylesheet(self):
        with self.assertRaises(ValueError):
            self.xslt_registry.register_stylesheet(
                'demo', 'play.xsl', os.path.join(cwd, 'play-invalid-xslt.xsl'))

    def test_register_nonexisting_stylesheet(self):
        with self.assertRaises(ValueError):
            self.xslt_registry.register_stylesheet(
                'demo', 'play.xsl', 'does.not.exist.xsl')

    def test_registry_clear(self):
        self._register_one()
        self.xslt_registry.clear()
        self.assertEqual(len(self.xslt_registry), 0)

    def test_registery_get_existing_xslt(self):
        self._register_one()
        self.xslt_registry.get_stylesheet('demo', 'play.xsl')

    def test_registery_get_nonexisting_xslt(self):
        self._register_one()
        with self.assertRaises(ValueError):
            self.xslt_registry.get_stylesheet('xxx', 'xxx')


class OtherTests(unittest2.TestCase):

    def test_parse_field_expression(self):

        from xmldirector.plonecore.dx.xpath_field import parse_field_expression as pfe
        self.assertEqual(pfe('field=xxxx,xpath=/a/bc'), ('xxxx', '/a/bc'))
        self.assertEqual(pfe('field=xxxx , xpath=/a/bc'), None)
        self.assertEqual(pfe(None), None)
        self.assertEqual(pfe(''), None)
        self.assertEqual(pfe('field,xpath'), None)


def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    suite.addTest(makeSuite(OtherTests))
    return suite
