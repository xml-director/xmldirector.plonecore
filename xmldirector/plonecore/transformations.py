# -*- coding: utf-8 -*-

################################################################
# onkopedia.policy
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import lxml.etree
from pp.core.transformation import registerTransformation


@registerTransformation
def addTableOfContentsForPDF(root, **params):
    """ Add a <section id="toc">..</section> containing links to
        as table of contents as first section of the document.
    """

    toc = list()
    for node in root.xpath('//*[self::h2 or self::h3 or self::h4 or self::h5]'):
        anchor = node.find('a')
        anchor_id = anchor.attrib['id']
        level = int(node.tag[1:]) - 1  # H2 -> H1...
        toc.append(
            u'<li><a class="level-{}" href="#{}">{}</a></li>'.format(level, anchor_id, anchor.text))

    toc_html = u'<ul id="toc-entries">' + u'\n'.join(toc) + u'</ul>'
    toc_headline = params['context'].translate('Table of contents',
                                               domain='onkopedia.policy',
                                               target_language=params['language'])
    html = u'<section id="toc"><span id="toc-title">{}</span>{}</section>'.format(
        toc_headline, toc_html)
    node = lxml.etree.fromstring(html)
    root.xpath('//body')[0].insert(0, node)


@registerTransformation
def exportImages(root, **params):
    """ Export images from eXist-db into the workdir """

    destdir = params['destdir']
    webdav_handle = params['context'].webdav_handle()

    # export raster image + svg
    for dirname in ('images/media', 'images/svg'):
        if webdav_handle.exists(dirname):
            for name in webdav_handle.listdir(dirname):
                with open(os.path.join(destdir, name), 'wb') as fp_out:
                    fp_out.write(
                        webdav_handle.open('{}/{}'.format(dirname, name), 'rb').read())

    # All images are exported into a flat structure.
    # So we need to adjust the relative image URLs.
    for node in root.xpath('//img'):
        src = node.attrib['src']
        node.attrib['src'] = src.split('/')[-1]

    for node in root.xpath('//object'):
        data = node.attrib['data']
        node.attrib['data'] = data.split('/')[-1]
