# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import plone.api
from .base import TestBase

from xmldirector.plonecore.dx import util
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

    def test_xml_image(self):

        from plone.namedfile import NamedImage

        img_data = open(os.path.join(os.path.dirname(__file__), 'sample.jpg'), 'rb').read()
        named_image = NamedImage()
        named_image.data = img_data
        named_image.filename = u'test.jpg'
        named_image.contentType = 'image/jpg'
        self.doc.xml_set('xml_image', named_image)

        named_image2 = self.doc.xml_get('xml_image')
        self.assertEqual(named_image2.data, img_data)
        self.assertEqual(named_image2.filename, u'test.jpg')
        self.assertEqual(named_image2.contentType, 'image/jpg')

    def test_xml_binary(self):

        from plone.namedfile import NamedFile

        img_data = open(os.path.join(os.path.dirname(__file__), 'sample.jpg'), 'rb').read()
        named_file = NamedFile()
        named_file.data = img_data
        named_file.filename = u'test.jpg'
        named_file.contentType = 'image/jpg'
        self.doc.xml_set('xml_binary', named_file)

        named_file2 = self.doc.xml_get('xml_binary')
        self.assertEqual(named_file2.data, img_data)
        self.assertEqual(named_file2.filename, u'test.jpg')
        self.assertEqual(named_file2.contentType, 'image/jpg')

    def test_copy_paste(self):

        xml = u'<?xml version="1.0" encoding="UTF-8"?>\n<hello>world</hello>'
        self.doc.xml_set('xml_content', xml)

        cb = self.portal.manage_copyObjects(self.doc.getId())
        self.portal.manage_pasteObjects(cb)
        copy_doc = self.portal['copy_of_dok']
        assert util.get_storage_key(self.doc) != util.get_storage_key(copy_doc)

    def test_remove(self):

        xml = u'<?xml version="1.0" encoding="UTF-8"?>\n<hello>world</hello>'
        self.doc.xml_set('xml_content', xml)

        self.portal.manage_delObjects(self.doc.getId())
        self.assertEqual('dok' not in self.portal.objectIds(), True)


def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    return suite
