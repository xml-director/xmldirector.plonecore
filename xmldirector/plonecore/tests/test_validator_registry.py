# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import unittest2
from xmldirector.plonecore.validator_registry import ValidatorRegistry

cwd = os.path.dirname(__file__)


class BasicTests(unittest2.TestCase):

    def setUp(self):
        self.registry = ValidatorRegistry()
        self.registry.clear()
        self.registry.parse_folder(
                family='testing',
                directory=os.path.join(cwd, 'schemas'))

    def test_parsing_improper_directory(self):
        with self.assertRaises(IOError):
            self.registry.parse_folder(
                    family='testing',
                    directory='does.not.exist')

    def test_registry(self):
        self.assertEquals(len(self.registry), 5)
        validator1 = self.registry[('testing', 'DGHO_Webcontent_20150202.dtd')]
        validator2 = self.registry['testing::DGHO_Webcontent_20150202.dtd']
        self.assertEqual(validator1, validator2)
        self.assertEqual(('testing', 'DGHO_Webcontent_20150202.dtd') in self.registry, True)

    def test_validator(self):
        validator = self.registry.get_validator(family='testing', name='simple.xsd')
        xml = open(os.path.join(cwd, 'simple.xml'), 'rb').read()
        result = validator.validate(xml)
        self.assertEqual(bool(result), True)

    def test_validator_wrong_xml(self):
        validator = self.registry.get_validator(family='testing', name='simple.xsd')
        xml = open(os.path.join(cwd, 'simple_bad.xml'), 'rb').read()
        result = validator.validate(xml)
        self.assertEqual(bool(result), False)

    def test_validator_with_DTD(self):
        validator = self.registry.get_validator(family='testing', name='simple.dtd')
        xml = open(os.path.join(cwd, 'simple_dtd.xml'), 'rb').read()
        result = validator.validate(xml)
        self.assertEqual(bool(result), True)

    def test_validator_with_RELAXNG(self):
        validator = self.registry.get_validator(family='testing', name='simple.rng')
        xml = open(os.path.join(cwd, 'simple_relaxng.xml'), 'rb').read()
        result = validator.validate(xml)
        self.assertEqual(bool(result), True)

    def test_validator_with_SCHEMATRON(self):
        validator = self.registry.get_validator(family='testing', name='simple.sch')
        xml = open(os.path.join(cwd, 'simple_schematron.xml'), 'rb').read()
        result = validator.validate(xml)
        self.assertEqual(bool(result), True)

    def test_validator_invalid_xml(self):
        validator = self.registry.get_validator(family='testing', name='simple.dtd')
        xml = open(os.path.join(cwd, 'simple_invalid.xml'), 'rb').read()
        result = validator.validate(xml)
        self.assertEqual(bool(result), False)

    def test_get_schema(self):
        validator = self.registry.get_schema(family='testing', name='DGHO_Webcontent_20150202.dtd')
        with self.assertRaises(ValueError):
            validator = self.registry.get_schema('testing', 'does.not.exist')


def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    return suite
