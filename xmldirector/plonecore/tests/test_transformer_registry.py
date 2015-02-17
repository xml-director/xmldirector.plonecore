# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import unittest2
import zExceptions
from xmldirector.plonecore.transformer_registry import TransformerRegistry
import Testing.makerequest
from base import TestBase

cwd = os.path.dirname(__file__)


def python_transformer(root, conversion_context):
    """ Sample Python transformation turning all <foo>
        tags into <bar> tags.
    """

    for node in root.xpath('//foo'):
        node.tag = 'bar'


class BasicTests(unittest2.TestCase):

    def setUp(self):
        self.registry = TransformerRegistry()
        self.registry.registry.clear()

    def _register_one(self):
        self.registry.register_transformation(
            'demo', 'play.xsl', os.path.join(cwd, 'play.xsl'), 'XSLT1')

    def test_register(self):
        self._register_one()

    def test_register_twice(self):
        self._register_one()
        with self.assertRaises(ValueError):
            self._register_one()

    def test_register_unsupported_transformer_type(self):
        with self.assertRaises(ValueError):
            self.registry.register_transformation(
                'demo', 'play.xsl', os.path.join(cwd, 'play.xsl'), 'XXXXXXXXXX')

    def test_register_invalid_xml_transformer(self):
        with self.assertRaises(ValueError):
            self.registry.register_transformation(
                'demo', 'play.xsl', os.path.join(cwd, 'play-invalid-xml.xsl'), 'XSLT1')

    def test_register_invalid_xslt_transformer(self):
        with self.assertRaises(ValueError):
            self.registry.register_transformation(
                'demo', 'play.xsl', os.path.join(cwd, 'play-invalid-xslt.xsl'), 'XSLT1')

    def test_register_nonexisting_transformer(self):
        with self.assertRaises(ValueError):
            self.registry.register_transformation(
                'demo', 'play.xsl', 'does.not.exist.xsl', 'XSLT1')

    def test_registry_clear(self):
        self._register_one()
        self.registry.clear()
        self.assertEqual(len(self.registry), 0)

    def test_registry_get_existing_xslt(self):
        self._register_one()
        self.registry.get_transformation('demo', 'play.xsl')

    def test_registry_get_nonexisting_xslt(self):
        self._register_one()
        with self.assertRaises(ValueError):
            self.registry.get_transformation('xxx', 'xxx')

    def test_register_python_transformer(self):
        self.registry.register_transformation(
            'demo', 'foo2bar replacer', python_transformer, 'python')

    def test_register_xslt2(self):
        self.registry.register_transformation(
            'xslt2', 'sample_xslt2.xsl', os.path.join(cwd, 'sample_xslt2.xsl'), 'XSLT2')


class ViewTests(TestBase):

    def setUp(self):
        super(ViewTests, self).setUp()
        self.registry = TransformerRegistry()
        self.registry.registry.clear()

    def _register_one(self):
        self.registry.register_transformation(
            'demo', 'play.xsl', os.path.join(cwd, 'play.xsl'), 'XSLT1')

    def test_transformer_registry_view_unauthorized(self):
        with self.assertRaises(zExceptions.Unauthorized):
            self.portal.restrictedTraverse('@@transformer-registry')

    def test_transformer_registry_view(self):
        self.login('god')
        view = self.portal.restrictedTraverse('@@transformer-registry')
        view()

    def test_transformer_registry_detail_view_unauthorized(self):
        with self.assertRaises(zExceptions.Unauthorized):
            self.portal.restrictedTraverse('@@transformer-registry-view')

    def test_transformer_registry_detail_view(self):
        self._register_one()
        self.login('god')
        Testing.makerequest.makerequest(self.portal)
        view = self.portal.restrictedTraverse('@@transformer-registry-view')
        self.portal.REQUEST.form['family'] = 'demo'
        self.portal.REQUEST.form['name'] = 'play.xsl'
        view()


def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    suite.addTest(makeSuite(ViewTests))
    return suite
