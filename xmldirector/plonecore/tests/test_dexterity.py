# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import plone.api
from .base import TestBase

from xmldirector.plonecore.dx.xpath_field import get_all_fields

class BasicTests(TestBase):

    def setUp(self):
        self.login('god')
        self.doc = plone.api.content.create(type='xmldirector.plonecore.xmldocument', container=self.portal, id='dok')

    def test_xmldocument(self):
        fields = get_all_fields(self.doc)
        self.assertEqual('xml_content' in fields, True)
        self.assertEqual('xml_xpath' in fields, True)
        self.assertEqual('xml_binary' in fields, True)
        self.assertEqual('xml_image' in fields, True)

    def test_set_with_valid_xml(self): 
        xml = u'<?xml version="1.0" encoding="UTF-8"?>\n<hello>world</hello>'
        self.doc.xml_set('xml_content', xml)
        xml2 = self.doc.xml_get('xml_content')
        self.assertEqual(xml, xml2)

    def test_with_invalid_fieldname(self):
        with self.assertRaises(ValueError):
            self.doc.xml_get('unknown')
        with self.assertRaises(ValueError):
            self.doc.xml_set('unknown', 'some xml')

    def test_with_invalid_xml(self):
        invalid_xml = u'this is not xml'
        with self.assertRaises(ValueError):
            self.doc.xml_set('xml_content', invalid_xml)


def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    return suite
