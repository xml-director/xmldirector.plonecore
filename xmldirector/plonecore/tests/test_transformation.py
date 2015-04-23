# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import codecs
import defusedxml.lxml
import unittest2
from xmldirector.plonecore.transformer_registry import TransformerRegistry
from xmldirector.plonecore.transformation import Transformer

cwd = os.path.dirname(__file__)


sample_xml = u'''<?xml version="1.0"?>
<hello>
    <world>
        <foo>123</foo>
        <foo>345</foo>
        <foo>789</foo>
    </world>
    <umlaute>mit Umlauten üöäßÜÖÄ</umlaute>
</hello>
'''


def python_transformer(root, conversion_context):
    """ Sample Python transformation turning all <foo>
        tags into <bar> tags.
    """

    for node in root.xpath('//foo'):
        node.tag = 'bar'


def python_transformer2(root, conversion_context):
    """ Sample Python transformation removing all <foo>
        nodes and putting an attribute foo="bar" into
        the root node
    """
    for node in root.xpath('//foo'):
        node.getparent().remove(node)
    root.attrib['foo'] = 'bar'


sample_xslt2 = os.path.join(cwd, 'sample_xslt2.xsl')
with codecs.open(os.path.join(cwd, 'sample_xslt2.xml'), 'rb', encoding='utf8') as fp:
    sample_xslt2_xml = fp.read()

catalog_xsl = os.path.join(cwd, 'catalog.xsl')
with codecs.open(os.path.join(cwd, 'catalog.xml'), 'rb', encoding='utf8') as fp:
    catalog_xml = fp.read()


def catalog_transformer(root, conversion_context):
    """ Sample Python transformation turning the result
        HTML of the catalog.xsd: replaces <table>
        with <TABELLE>.
    """
    for node in root.xpath('//table'):
        node.tag = 'TABELLE'


class BasicTests(unittest2.TestCase):

    def setUp(self):
        self.registry = TransformerRegistry()
        self.registry.clear()
        self.registry.register_transformation(
            'demo', 't1', python_transformer, 'python')
        self.registry.register_transformation(
            'demo', 't2', python_transformer2, 'python')
        self.registry.register_transformation(
            'demo', 'catalog-xsl', catalog_xsl, 'XSLT1')
        self.registry.register_transformation(
            'demo', 'sample-xslt2', sample_xslt2, 'XSLT2')
        self.registry.register_transformation(
            'demo', 'catalog-python', catalog_transformer, 'python')

    def test_verify_steps_working(self):
        T = Transformer(
            [('demo', 't1'), ('demo', 't2')], transformer_registry=self.registry)
        T.verify_steps()

    def test_verify_steps_failing(self):
        T = Transformer([('xxx', 'yyy')], transformer_registry=self.registry)
        with self.assertRaises(ValueError):
            T.verify_steps()

    def test_transformation_1(self):
        T = Transformer([('demo', 't1')], transformer_registry=self.registry)
        result = T(sample_xml)
        self.assertTrue(result.count('<bar>') == 3)

    def test_transformation_with_node(self):
        T = Transformer([('demo', 't1')], transformer_registry=self.registry)
        result = T(defusedxml.lxml.fromstring(sample_xml))
        self.assertTrue(result.count('<bar>') == 3)

    def test_transformation_improper_root(self):
        T = Transformer([('demo', 't1')], transformer_registry=self.registry)
        with self.assertRaises(TypeError):
            T(object)

    def test_transformation_unicode_without_input_encoding(self):
        T = Transformer([('demo', 't1')], transformer_registry=self.registry)
        with self.assertRaises(TypeError):
            T(sample_xml.encode('utf8'), input_encoding=None)

    def test_transformation_2(self):
        T = Transformer([('demo', 't2')], transformer_registry=self.registry)
        result = T(sample_xml)
        self.assertTrue('<hello foo="bar">' in result)

    def test_transformation_return_fragment(self):
        T = Transformer([('demo', 't1')], transformer_registry=self.registry)
        result = T(sample_xml, return_fragment='world')
        self.assertTrue('<hello' not in result)

    def test_transformation_return_fragment_non_existing_fragment(self):
        T = Transformer([('demo', 't1')], transformer_registry=self.registry)
        with self.assertRaises(ValueError):
            T(sample_xml, return_fragment='XXXXXX')

    def test_transformation_custom_output_encoding(self):
        T = Transformer([('demo', 't1')], transformer_registry=self.registry)
        result = T(sample_xml, output_encoding='utf16')
        self.assertTrue(not isinstance(result, unicode))

    def test_transformation_1_and_2(self):
        T = Transformer(
            [('demo', 't1'), ('demo', 't2')], transformer_registry=self.registry)
        result = T(sample_xml)
        self.assertTrue(result.count('<foo>') == 0)
        self.assertTrue(result.count('<bar>') == 3)
        self.assertTrue('<hello foo="bar">' in result)

    def test_catalog_xsd(self):
        T = Transformer(
            [('demo', 'catalog-xsl')], transformer_registry=self.registry)
        result = T(catalog_xml)
        self.assertTrue('<h2>My CD Collection</h2>' in result)
        self.assertTrue('<tr bgcolor="#9acd32">' in result)
        self.assertTrue('<td>Bob Dylan</td>' in result)

    def test_catalog_xsd_python_transform(self):
        T = Transformer([('demo', 'catalog-xsl'),
                         ('demo', 'catalog-python')],
                        transformer_registry=self.registry)
        result = T(catalog_xml)
        self.assertTrue('<h2>My CD Collection</h2>' in result)
        self.assertTrue('<tr bgcolor="#9acd32">' in result)
        self.assertFalse('<table>' in result)
        self.assertTrue('<TABELLE' in result)

    def test_transformation_with_debug_option(self):
        T = Transformer([('demo', 'catalog-xsl'),
                         ('demo', 'catalog-python')],
                        transformer_registry=self.registry)
        T(catalog_xml, debug=True)

    def test_catalog_python_xsd_transform(self):
        T = Transformer([('demo', 'catalog-python'),
                         ('demo', 'catalog-xsl')],
                        transformer_registry=self.registry)
        result = T(catalog_xml)
        # running catalog-python first should not have any effect
        self.assertTrue('<h2>My CD Collection</h2>' in result)
        self.assertTrue('<tr bgcolor="#9acd32">' in result)
        self.assertTrue('<table' in result)

    def test_xslt2_transformation(self):
        T = Transformer([('demo', 'sample-xslt2')],
                        transformer_registry=self.registry)
        result = T(sample_xslt2_xml)
        self.assertTrue('<test xmlns="http://www.example.com/v2">' in result)


def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    return suite
