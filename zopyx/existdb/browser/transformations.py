################################################################
# zopyx.existdb
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################

import os
import lxml
import cgi
import re
import PIL.Image
from cStringIO import StringIO
from pp.client.plone.logger import LOG
from pp.client.plone.browser.images import resolveImage
from pp.core.transformation import registerTransformation
from lxml.cssselect import CSSSelector
from Products.CMFCore.utils import getToolByName


url_match = re.compile(r'^(http|https|ftp)://')
ALL_HEADINGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10')

def xpath_query(node_names):
    if not isinstance(node_names, (list, tuple)):
        raise TypeError('"node_names" must be a list or tuple (not %s)' % type(node_names))
    return './/*[%s]' % ' or '.join(['name()="%s"' % name for name in node_names])

@registerTransformation
def makeImagesLocal(root, params, errors):
    """ deal with internal and external image references """

    ref_catalog = getToolByName(params['context'], 'reference_catalog')
    destdir = params['destdir']

    images_seen = dict()
    for img in root.xpath(xpath_query(['img'])):

        # don't touch images with attribute internal-image="true" (usually used
        # for resource images directly used in a template with a resource
        if 'internal-image' in img.attrib:
            continue

        src = img.get('src')
        LOG.info('Introspecting image: {}'.format(src))
        result = resolveImage(params['context'], src)
        img_obj =  result['image']

        if img_obj is None:
            LOG.error('Image {} count not be resolved'.format(src))
            errors.append(u'Image missing ({})'.format(src))
            # replace <img> with error <div>
            div = lxml.html.Element('div')
            div.attrib['class'] = 'missing-image'
            div.text = u'Image {} not resolvable'.format(src)
            img.getparent().replace(img, div)
            continue

        # resolved did find a local image
        LOG.info('  Local processing: %s' % src)
        current= images_seen.get(src)

        if not current:

            # assume that this is the primary image object in Plone
            img_data = str(img_obj.data)

            # determine graphic format using PIL
            pil_image = PIL.Image.open(StringIO(img_data))
            format = pil_image.format.lower()
            width, height = pil_image.size

            # generate unique and speaking image names
            img_id = '{}.{}'.format(img_obj.getId(), format) 
            dest_img_name = os.path.join(destdir, img_id)
            with open(dest_img_name, 'wb') as fp:
                fp.write(img_data)

            images_seen[src] = current = dict(width=width,
                                              height=height,
                                              id=img_id,
                                              format=format,
                                              filename=dest_img_name)

        try:                
            img_title = img_obj.Title()
        except AttributeError:
            img_title = u''
        if not isinstance(img_title, unicode):
            img_title = unicode(img_title, 'utf-8')
        try:                
            img_description = img_obj.Description()
        except AttributeError:
            img_description = u''
        if not isinstance(img_description, unicode):
            img_description = unicode(img_description, 'utf-8')

        # now move <img> tag into a dedicated <div>
        figure = lxml.html.Element('figure')
        new_img =  lxml.html.Element('img')
        # preserve original attributes
        new_img.attrib.update(img.attrib.items())
        new_img.attrib['src'] = img_id
        new_img.attrib['format'] = current['format']
        new_img.attrib['height'] = str(current['height'])
        new_img.attrib['width'] = str(current['width'])
        new_img.attrib['description'] = img_description

        figure.append(new_img)
        figcaption =  lxml.html.Element('figcaption')
        figcaption.attrib['title'] = img_title
        figcaption.text = img_description
        figure.append(figcaption)
        img.getparent().replace(img, figure)

url_match = re.compile(r'^(http|https|ftp)://')

@registerTransformation
def convertFootnotes(root):

    # Special format for footnotes:
    # <span class="footnoteText">some footnote text</span>

    for node in CSSSelector('span.footnoteText')(root):
        footnote_text = node.text_content()
        if footnote_text:
            node.attrib['class'] = 'generated-footnote'

    # generate footnotes from <a href>...</a> fields
    for a in root.xpath('//a'):
        href = a.get('href', '')
        if not href or not url_match.match(href) or 'editlink' in a.get('class', ''):
            continue

        text = a.text_content().strip()
        if text:
            # don't convert URL links with an URL as pcdata into a footnote
            if url_match.match(text):
                continue
            new_a = lxml.html.Element('a')
            new_a.text = cgi.escape(href)
            new_a.attrib['href'] = href

            span = lxml.html.Element('span')
            span.attrib['class'] = 'generated-footnote'
            span.append(new_a)

            span2 = lxml.html.Element('span')
            span2.attrib['class'] = 'generated-footnote-text'
            span2.text = text
            span2.append(span)

            a.getparent().replace(a, span2)

@registerTransformation
def removeCrapFromHeadings(root):
    """ Ensure that HX tags containing only text """

    for node in root.xpath(xpath_query(ALL_HEADINGS)):
        text = node.text_content()
        if text:
            node.clear()
            node.text = text
        else:
            node.getparent().remove(node)

@registerTransformation
def fixHierarchies(root):
    """ Iterate of all boundary documents. For documents
        with level > 0 we need to shift to hierarchies down.
    """

    for doc in root.xpath('//div'):
        if not 'document-boundary' in doc.get('class', ''):
            continue
        level = int(doc.get('level', '0'))
        if level > 0:
            for heading in doc.xpath(xpath_query(ALL_HEADINGS)):
                heading_level = int(heading.tag[-1])
                heading.tag = 'h%d' % (heading_level + level)

@registerTransformation
def addTableOfContents(root):
    """ Add a table of contents to the #toc node """

    toc = list()

    # first find all related entries (.bookmark-title class)
    for count, e in enumerate(root.xpath(xpath_query(ALL_HEADINGS))):
        level = int(e.tag[-1]) - 1 # in Plone everything starts with H2
        text = e.text_content()
        id = 'toc-%d' % count
        new_anchor = lxml.html.Element('a')
        new_anchor.attrib['name'] = id
        e.insert(0, new_anchor)
        toc.append(dict(text=text,
                        level=level,
                        id=id))

    div_toc = lxml.html.Element('div')
    div_toc.attrib['id'] = 'toc'
    div_ul = lxml.html.Element('ul')
    div_toc.append(div_ul)

    for d in toc:
        li = lxml.html.Element('li')
        li.attrib['class'] = 'toc-%s' % d['level']
        a = lxml.html.Element('a')
        a.attrib['href'] = '#' + d['id']
        a.attrib['class'] = 'toc-%s' % d['level']
        span = lxml.html.Element('span')
        span.text = d['text']
        a.insert(0, span)
        li.append(a)
        div_ul.append(li)

    # check for an existing TOC (div#toc) 
    nodes = CSSSelector('div#toc')(root)
    if nodes:
        # replace it with the generated TOC
        toc = nodes[0]
        toc.getparent().replace(toc, div_toc)
    else:
        # append generated TOC to body tag
        body = root.xpath('//body')[0]
        body.insert(0, div_toc)

@registerTransformation
def adjustHeadingsFromAggregatedHTML(root):
    """ For an aggregated HTML documented from a nested folder
        structure we need to adjust the HX headings of the contained
        AuthoringContentPage documents. The 'level' attribute of the
        related document nodes is taken as an offset for recalculating
        the headings.
    """

    # search all documents first
    selector = CSSSelector('div.portal-type-authoringcontentpage')
    for node in selector(root):    
        # get their level
        level = int(node.get('level'))

        # create a sorted list of used headings
        heading_levels_used = list()
        for heading in node.xpath(xpath_query(ALL_HEADINGS)):
            heading_level = int(heading.tag[1:])
            if not heading_level in heading_levels_used:
                heading_levels_used.append(heading_level)
        heading_levels_used.sort()

        # now add an offset to the heading level
        for heading in node.xpath(xpath_query(ALL_HEADINGS)):
            heading_level = int(heading.tag[1:])
            new_level = level + heading_levels_used.index(heading_level) 
            heading.tag = 'h%d' % new_level

@registerTransformation
def shiftHeadings(root):
    """ H1 -> H2, H2 -> H3.... """
    for node in root.xpath(xpath_query(ALL_HEADINGS)):
        level = int(node.tag[1:])
        node.tag = 'h%d' % (level+1)

