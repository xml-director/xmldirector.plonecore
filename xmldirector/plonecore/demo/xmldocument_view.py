# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import lxml.etree
import lxml.html.clean
import zope.component
from Products.Five.browser import BrowserView
from xmldirector.plonecore.interfaces import IXSLTRegistry


class XMLDocument(BrowserView):

    def xslt_transform(self, fieldname, family, stylesheet_name):
        """ Perform an XSLT registration for the XML stored on the current
            context object under a given registered XSLT transformation.
        """

        registry = zope.component.getUtility(IXSLTRegistry)
        xml = self.context.xml_get(fieldname)
        if not xml:
            return u''
        transform = registry.get_stylesheet(family, stylesheet_name)
        doc_root = lxml.etree.fromstring(xml)
        result = transform(doc_root)
        html = lxml.etree.tostring(result.getroot(), encoding=unicode)
        cleaner = lxml.html.clean.Cleaner()
        return cleaner.clean_html(html)

    def asHTML(self):
        """ Generate a demo PDF """
        return self.xslt_transform('xml_content', 'demo', 'play.xsl')

