import lxml.etree


xslt_root = lxml.etree.XML(open('play.xsl', 'rb').read())
transform = lxml.etree.XSLT(xslt_root)

doc = lxml.etree.parse(open('winters_tale.xml', 'rb'))

tree = transform(doc)
import pdb; pdb.set_trace() 

print lxml.etree.tostring(tree)
