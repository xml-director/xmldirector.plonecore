################################################################
# zopyx.existdb
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################

import os
import codecs
from cStringIO import StringIO
from BeautifulSoup import BeautifulSoup, Tag

from lxml.cssselect import CSSSelector
import lxml.html 

from util import _findTextInNode

def split_html(html_filename, split_at_level=0):
    """ Split aggregated and rendered HTML document at
        some <hX> tag(s). split_at_level=0 -> split at
        H1 tags, split_at_level=1 -> split at H1 and H2
        tags.
        Returns a list of dicts with keys 'html' referring
        to the subdocument and 'level' indicating the split
        point.
    """

    destdir = os.path.dirname(html_filename)
    soup = BeautifulSoup(file(html_filename).read())
    fp = StringIO(soup.__str__(prettyPrint=True))
    docs = list()
    current_doc = list()
    for line in fp:
        line = line.rstrip()
        for level in range(split_at_level+1):
            if '<h%d' % (level+1) in line.lower():
                html = '\n'.join(current_doc)
                root = lxml.html.fromstring(unicode(html, 'utf-8'))
                title = u''
                h1_nodes = root.xpath('//h1')
                if h1_nodes:
                    title = h1_nodes[0].text_content().strip()

                # count tables and images
                number_tables = len(root.xpath('//table'))
                number_images = len(CSSSelector('div.image-caption')(root))

                # find all linkable nodes with an ID attribute
                node_ids = list()
                for node in root.xpath('.//*'):
                    node_id = node.get('id')
                    if node_id:
                        node_ids.append(node_id)

                html = lxml.html.tostring(root, encoding=unicode)
                docs.append(dict(html=html, 
                                 level=level, 
                                 title=title, 
                                 node_ids=node_ids,
                                 number_images=number_images,
                                 number_tables=number_tables))
                current_doc = []
                break
                
        current_doc.append(line)

    # now deal with the remaining part of the document
    html = '\n'.join(current_doc)
    root = lxml.html.fromstring(unicode(html, 'utf-8'))
    title = u''
    h1_nodes = root.xpath('//h1')
    if h1_nodes:
        title = h1_nodes[0].text_content().strip()

    # count tables and images
    # count tables and images
    number_tables = len(root.xpath('//table'))
    number_images = len(CSSSelector('div.image-caption')(root))

    # find all linkable nodes with an ID attribute
    node_ids = list()
    for node in root.xpath('.//*'):
        node_id = node.get('id')
        if node_id:
            node_ids.append(node_id)

    html = lxml.html.tostring(root, encoding=unicode)
    docs.append(dict(html=html, 
                     level=0, 
                     title=title, 
                     node_ids=node_ids,
                     number_images=number_images,
                     number_tables=number_tables))

    # now store files on the filesystem
    ini_filename = os.path.join(destdir, 'documents.ini')
    fp_ini = codecs.open(ini_filename, 'w', 'utf-8')

    for count, d in enumerate(docs[1:]):
        filename = os.path.join(destdir, 'split-0/%d-level-%d.html' % (count, d['level']))
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))                
        file(filename, 'w').write(d['html'].encode('utf-8'))

        print >>fp_ini, '[%d]' % count
        print >>fp_ini, 'filename = %s' % filename
        print >>fp_ini, 'title = %s' % d['title']
        print >>fp_ini, 'number_tables= %d' % d['number_tables']
        print >>fp_ini, 'number_images = %d' % d['number_images']
        print >>fp_ini, 'node_ids = '
        for node_id in d['node_ids']:
            print >>fp_ini, '    ' + node_id
        print >>fp_ini 

    fp_ini.close()
    return docs[1:]
