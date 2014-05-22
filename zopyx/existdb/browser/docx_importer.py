################################################################
# zopyx.existdb
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################

import cssutils
import os
import lxml
import base64
from cStringIO import StringIO
import PIL.Image
from datetime import datetime
from Products.Five.browser import BrowserView
from pp.client.python.unoconv import unoconv
from pp.client.plone.logger import LOG
import tempfile
import zipfile

ignored_styles = (
    'font-family',
    'orphans',
    'direction',
    'widows',
    'border',
    'border-top',
    'border-bottom',
    'border-left',
    'border-right',
    'padding',
    'padding-top',
    'padding-bottom',
    'padding-left',
    'padding-right',
    'margin',
    'margin-top',
    'margin-bottom',
    'margin-left',
    'margin-right',
    'so-language',
    'page-break-before',
    'page-break-after',
    'font-size', 
    'text-indent',
    'line-height',
)

def cleanup_css(css):
    sheet = cssutils.parseString(css)
    cssutils.ser.prefs.indent = '  '
    
    for i, rule in enumerate(sheet):
        if isinstance(rule, cssutils.css.CSSStyleRule):
            remove_props = list()
            remove_props = [prop.name for prop in rule.style if prop.name.lower() in ignored_styles]
            for name in remove_props:
                rule.style.removeProperty(name)

    for i, rule in enumerate(sheet):
        if isinstance(rule, cssutils.css.CSSPageRule):
            sheet.deleteRule(rule)
            continue

    return sheet.cssText

class DocxImporter(BrowserView):

    def view_docx(self):
        styles = self.context.getFolderContents({
            'portal_type': 'File',
            'sort_on': 'getObjPositionInParent'},
            full_objects=True)
        styles = [s for s in styles if s.getId().endswith('.css')]
        styles = u'\n'.join(str(s.getFile()) for s in styles)
        html = self.context['index.html'].getText()
        return dict(styles=styles, html=html)

    def _cleanup_after_import(self, source_filename):
        """ Cleanup import folder and change names """

        html = self.context[source_filename].getRawText()
        
        # tidy first
        filename = tempfile.mktemp()
        filename_out = filename + '.out'
        with open(filename, 'wb') as fp:
            fp.write(html)
        cmd = 'tidy -utf8 -c %s >%s' % (filename, filename_out)
        LOG.info('Running %s' % cmd)
        status = os.system(cmd)
        LOG.info('tidy exit code: %d' % status)
        if not os.path.exists(filename_out) or os.path.getsize(filename_out) == 0:
            raise RuntimeError('Running "tidy" failed (cmd: %s)' % cmd)
        with open(filename_out, 'rb') as fp:
            html = fp.read()
        os.unlink(filename)
        os.unlink(filename_out)

        # parse HTML into DOM
        root = lxml.html.fromstring(html)

        # export base64 encoded inline images
        base64_marker = 'data:image/*;base64,'
        count = 1
        for img in root.xpath('//img'):
            src = img.attrib['src']
            if src.startswith(base64_marker):
                img_data = base64.decodestring(src.replace(base64_marker, ''))
                pil_image = PIL.Image.open(StringIO(img_data))
                fmt = pil_image.format.lower()
                if fmt in ('wmf'):
                    raise RuntimeError('Word document must not contain embeed WMF files')
                new_id = 'tmp{0:d}.png'.format(count)
                self.context.invokeFactory('Image', id=new_id)
                new_image = self.context[new_id]
                new_image.setTitle(new_id)
                out = StringIO()
                pil_image.save(out, format='PNG')
                new_image.setImage(out.getvalue())
                new_image.reindexObject()
                img.attrib['src'] = new_id
                count += 1

        # rename images
        images_seen = dict()
        count = 1
        for img in root.xpath('//img'):
            src = img.attrib['src']
            base, ext = os.path.splitext(src)
            if not src in images_seen:
                new_id = '{0:d}{1:s}'.format(count, ext)
                images_seen[src] = new_id
                self.context[src].unindexObject()
                self.context.manage_renameObject(src, new_id)
                self.context[new_id].setTitle(new_id)
                self.context[new_id].indexObject()
                count += 1
            else:
                new_id = images_seen[src]
            img.attrib['src'] = new_id

        # export styles
        for i, style in enumerate(root.xpath('//style')):
            style_css = cleanup_css(style.text)
            style_id = '{0:d}.css'.format(i + 1)
            self.context.invokeFactory('File', id=style_id)
            self.context[style_id].setFile(style_css)
            self.context[style_id].setContentType('text/css')
            self.context[style_id].reindexObject()

        body = root.xpath('//body')[0]
        self.context[source_filename].setText(lxml.html.tostring(body, unicode))
        self.context[source_filename].unindexObject()
        self.context.manage_renameObject(source_filename, 'index.html')
        self.context['index.html'].setTitle('index.html')
        self.context['index.html'].reindexObject()


    def docx_import(self):

        prefix = '{0}-{1}'.format(self.context.getId(), datetime.now().strftime('%Y%d%m-%H%M%S'))
        zip_in = tempfile.mktemp(prefix=prefix, suffix='.zip')
        with open(zip_in, 'wb') as zf:
            zf.write(self.request.form['doc'].read())
        
        # convert using unoconv
        zip_out = tempfile.mktemp(suffix='.zip')
        result = unoconv(zip_in, format='xhtml', output=zip_out)
        if result['status'] != 'OK':
            self.context.plone_utils.addPortalMessage(u'Error during import')
            return self.request.response.redirect(self.context.absolute_url() + '/docx-import-form')

        # remove old content first
        self.context.manage_delObjects(self.context.objectIds())

        zf = zipfile.ZipFile(zip_out, 'r')
        source_filename = None
        for name in zf.namelist():
            print name
            base, ext = os.path.splitext(name)
            if ext in ('.html',):
                self.context.invokeFactory('Document', id=name)
                source_filename = name
                doc = self.context[name]
                doc.setTitle(name)
                doc.setText(zf.read(name))
                doc.reindexObject()
                LOG.info('Imported {0}'.format(name))
            elif ext in ('.gif', '.png', '.jpeg', '.jpg'):
                self.context.invokeFactory('Image', id=name)
                doc = self.context[name]
                doc.setTitle(name)
                doc.setImage(zf.read(name))
                doc.reindexObject()
                LOG.info('Imported {0}'.format(name))

        self._cleanup_after_import(source_filename)
        self.context.plone_utils.addPortalMessage(u'Import successfull')
        self.request.response.redirect(self.context.absolute_url() + '/folder_contents')
