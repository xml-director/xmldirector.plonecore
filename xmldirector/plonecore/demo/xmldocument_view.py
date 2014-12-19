################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import lxml.etree
import lxml.html.clean
from Products.Five.browser import BrowserView
from xmldirector.plonecore import xslt_registry


class XMLDocument(BrowserView):

    def xslt_transform(self, fieldname, family, stylesheet_name):
        """ Perform an XSLT registration for the XML stored on the current
            context object under a given registered XSLT transformation.
        """

        xml = self.context.xml_get(fieldname)
        transform = xslt_registry.get_stylesheet(family, stylesheet_name)
        doc_root = lxml.etree.fromstring(xml)
        result = transform(doc_root)
        html = lxml.etree.tostring(result.getroot(), encoding=unicode)
        cleaner = lxml.html.clean.Cleaner()
        return cleaner.clean_html(html)
