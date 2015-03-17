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
from xmldirector.plonecore.dx.xpath_field import get_all_xml_fields


class BasicTests(TestBase):

    def setUp(self):
        self.login('god')
        self.doc = plone.api.content.create(
            type='xmldirector.plonecore.xmldocument', container=self.portal, id='dok')

    def test_xmldocument(self):
        fields = get_all_fields(self.doc)
        self.assertEqual('xml_content' in fields, True)
        self.assertEqual('xml_xpath' in fields, True)
        self.assertEqual('xml_binary' in fields, True)
        self.assertEqual('xml_image' in fields, True)

        xml_fields = get_all_xml_fields(self.doc)
        field_names = set(f.getName() for f in xml_fields)
        self.assertEqual('xml_binary' in field_names, True)
        self.assertEqual('xml_content' in field_names, True)
        self.assertEqual('xml_image' in field_names, True)

    def test_set_with_valid_xml(self):
        xml = u'<?xml version="1.0" encoding="UTF-8"?>\n<hello>world</hello>'
        self.doc.xml_set('xml_content', xml)
        xml2 = self.doc.xml_get('xml_content')
        self.assertEqual(xml2.endswith('<hello>world</hello>'), True)

    def test_set_reset_with_None(self):
        xml = u'<?xml version="1.0" encoding="UTF-8"?>\n<hello>world</hello>'
        self.doc.xml_set('xml_content', xml)
        self.doc.xml_set('xml_content', None)
        self.assertEqual(self.doc.xml_get('xml_content'), None)

    def test_set_with_None(self):
        self.doc.xml_set('xml_content', None)
        self.assertEqual(self.doc.xml_get('xml_content'), None)

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

        img_data = open(
            os.path.join(os.path.dirname(__file__), 'sample.jpg'), 'rb').read()
        named_image = NamedImage()
        named_image.data = img_data
        named_image.filename = u'üöä.jpg'
        named_image.contentType = 'image/jpg'
        self.doc.xml_set('xml_image', named_image)

        named_image2 = self.doc.xml_get('xml_image')
        self.assertEqual(named_image2.data, img_data)
        self.assertEqual(named_image2.filename, u'üöä.jpg')
        self.assertEqual(named_image2.contentType, 'image/jpg')

    def test_xml_binary(self):

        from plone.namedfile import NamedFile

        img_data = open(
            os.path.join(os.path.dirname(__file__), 'sample.jpg'), 'rb').read()
        named_file = NamedFile()
        named_file.data = img_data
        named_file.filename = u'üöä.jpg'
        named_file.contentType = 'image/jpg'
        self.doc.xml_set('xml_binary', named_file)

        named_file2 = self.doc.xml_get('xml_binary')
        self.assertEqual(named_file2.data, img_data)
        self.assertEqual(named_file2.filename, u'üöä.jpg')
        self.assertEqual(named_file2.contentType, 'image/jpg')

    def test_xml_binary_set_None(self):
        self.doc.xml_set('xml_binary', None)
        result = self.doc.xml_get('xml_binary')
        self.assertEqual(result, None)

    def test_xpath_field(self):
        self.doc.xml_set(
            'xml_content', u'<root><a>hello</a><a>world</a></root>')
        self.doc.xml_set('xml_xpath', u'field=xml_content,xpath=//a/text()')
        result = self.doc.xml_get('xml_xpath', raw=False)
        self.assertEqual(result, [u'hello', u'world'])
        self.assertEqual(
            self.doc.xml_xpath, u'field=xml_content,xpath=//a/text()')

    def test_xpath_field_improper_spec(self):
        spec = u'xx'
        with self.assertRaises(ValueError):
            spec = u'xx'
            self.doc.xml_set('xml_xpath', spec)
        with self.assertRaises(ValueError):
            spec = u'field=abc, xpath=ööööö'
            self.doc.xml_set('xml_xpath', spec)

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

    def test_metadata_to_xml_plone_root(self):

        from xmldirector.plonecore.dx import util

        xml = util.metadata_to_xml(self.portal)
        metadata = util.xml_to_metadata(xml)
        self.assertEqual(metadata['plone-path'], '/plone')
        self.assertEqual(metadata['plone-uid'], None)

    def test_views(self):
        self.doc.restrictedTraverse('@@view')()
        self.doc.restrictedTraverse('@@edit')()


def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(BasicTests))
    return suite
