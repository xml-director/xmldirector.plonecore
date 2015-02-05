# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import unittest2
from xmldirector.plonecore.schema_registry import SchemaRegistry

cwd = os.path.dirname(__file__)


class BasicTests(unittest2.TestCase):

    def setUp(self):
        self.registry = SchemaRegistry()
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
        self.assertEquals(len(self.registry), 1)
        validator1 = self.registry[('testing', 'DGHO_Webcontent_20150202.dtd')]
        validator2 = self.registry['testing::DGHO_Webcontent_20150202.dtd']
        self.assertEqual(validator1, validator2)
        self.assertEqual(('testing', 'DGHO_Webcontent_20150202.dtd') in self.registry, True)

    def test_get_schema(self):
        validator = self.registry.get_schema('testing', 'DGHO_Webcontent_20150202.dtd')
        with self.assertRaises(ValueError):
            validator = self.registry.get_schema('testing', 'does.not.exist')



def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    return suite
