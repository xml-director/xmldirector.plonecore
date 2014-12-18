################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import os
import lxml.etree
from Products.Five.browser import BrowserView


class XMLDocument(BrowserView):

    def xslt_transform(self, fieldname, stylesheet_filename):

        xml = self.context.xml_get(fieldname)
        with open(os.path.join(os.path.dirname(__file__), stylesheet_filename), 'rb') as fp:
            xslt_tree = lxml.etree.XML(fp.read())
            transform = lxml.etree.XSLT(xslt_tree)
            doc_root = lxml.etree.fromstring(xml)
            result = transform(doc_root)
            return lxml.etree.tostring(result.getroot(), encoding=unicode)

