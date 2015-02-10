# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import unittest2
from xmldirector.plonecore.transformer_registry import TransformerRegistry
from xmldirector.plonecore.transformation import Transformer

cwd = os.path.dirname(__file__)


sample_xml = u'''<?xml version="1.0">
<hello>
    <world>
        <foo>123</foo>
        <foo>345</foo>
        <foo>789</foo>
    </world>
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


class BasicTests(unittest2.TestCase):

    def setUp(self):
        self.registry = TransformerRegistry()
        self.registry.clear()
        self.registry.register_transformation(
                'demo', 't1', python_transformer, 'python')
        self.registry.register_transformation(
                'demo', 't2', python_transformer2, 'python')

    def test_verify_steps_failing(self):
        T = Transformer([('demo', 't1'), ('demo', 't2')], transformer_registry=self.registry)
        T.verify_steps()

    def test_verify_steps_failing(self):
        T = Transformer([('xxx', 'yyy')], transformer_registry=self.registry)
        with self.assertRaises(ValueError):
            T.verify_steps()

    def test_transformation_1(self):
        T = Transformer([('demo', 't1')], transformer_registry=self.registry)
        result = T(sample_xml)
        self.assertTrue(result.count('<bar>') == 3)

    def test_transformation_2(self):
        T = Transformer([('demo', 't2')], transformer_registry=self.registry)
        result = T(sample_xml)
        self.assertTrue('<hello foo="bar">' in result)

    def test_transformation_1_and_2(self):
        T = Transformer([('demo', 't1'), ('demo', 't2')], transformer_registry=self.registry)
        result = T(sample_xml)
        self.assertTrue(result.count('<foo>') == 0)
        self.assertTrue(result.count('<bar>') == 3)
        self.assertTrue('<hello foo="bar">' in result)


def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    return suite
