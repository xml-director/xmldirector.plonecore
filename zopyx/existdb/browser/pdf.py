################################################################
# zopyx.existdb
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################

import os
import codecs
import shutil
import tempfile
import zipfile

from compatible import InitializeClass
from Products.Five.browser import BrowserView
from Products.ATContentTypes.interface.folder import IATFolder
from ZPublisher.Iterators import filestream_iterator
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile 
from zope.pagetemplate.pagetemplatefile import PageTemplate

from pp.client.plone.logger import LOG
from pp.core.transformation import Transformer
from pp.core.resources_registry import getResource

from util import getLanguageForObject

cwd = os.path.dirname(os.path.abspath(__file__))

# server host/port of the SmartPrintNG server
DEFAULT_CONVERTER = os.environ.get('PP_CONVERTER', 'princexml')
DEFAULT_RESOURCE = os.environ.get('PP_RESOURCE', 'pp-default')
SERVER_URL = os.environ.get('PP_SERVER_URL', 'http://localhost:6543')
ZIP_OUTPUT = 'PP_ZIP_OUTPUT' in os.environ


class ProducePublishView(BrowserView):
    """ Produce & Publish view (using Produce & Publish server) """

    # default transformations used for the default PDF view.
    # 'transformations' can be overriden within a derived ProducePublishView.
    # If you don't need any transformation -> redefine 'transformations'
    # as empty list or tuple

    transformations = (
        'makeImagesLocal',
        'convertFootnotes',
        'removeCrapFromHeadings',
        'fixHierarchies',
#        'addTableOfContents',
        )

    def __init__(self, context, request):
        self.request = request
        self.context = context

    @property
    def resource(self):
        resource_id = self.request.get('resource', DEFAULT_RESOURCE)
        try:
            return getResource(resource_id)
        except KeyError:
            raise KeyError(u'No resource "{}" registered'.format(resource_id))

    def copyResourceFiles(self, destdir):
        """ Copy over resources for a global or local resources directory into the 
            destination directory.
        """

        fslayer = self.resource.fslayer
        for dirname, filenames in fslayer.walk():
            for filename in filenames:
                fullpath = os.path.join(dirname, filename)
                with fslayer.open(fullpath, 'rb') as fp:
                    content = fp.read()

                if fullpath.startswith('/'):
                    fullpath = fullpath[1:]
                destpath = os.path.join(destdir, fullpath)
                if not os.path.exists(os.path.dirname(destpath)):
                    os.makedirs(os.path.dirname(destpath))
                with open(destpath, 'wb') as fp:
                    fp.write(content)

    def transformHtml(self, html, destdir, transformations=None):
        """ Perform post-rendering HTML transformations """

        if transformations is None:
            transformations = self.transformations

        # the request can override transformations as well
        if self.request.has_key('transformations'):
            t_from_request = self.request['transformations']
            if isinstance(t_from_request, basestring):
                transformations = t_from_request and t_from_request.split(',') or []
            else:
                transformations = t_from_request

        T = Transformer(transformations, 
                        context=self.context, 
                        destdir=destdir)
        return T(html)

    def __call__(self, *args, **kw):

        try:
            return self.__call2__(*args, **kw)
        except:
            LOG.error('Conversion failed', exc_info=True)
            raise


    def __call2__(self, *args, **kw):
        """ URL parameters:
            'language' -  'de', 'en'....used to override the language of the
                          document
            'converter' - default to on the converters registered with
                          zopyx.convert2 (default: pdf-prince)
            'resource' - the name of a registered resource (directory)
            'template' - the name of a custom template name within the choosen
                         'resource' 
        """

        # Output directory
        tmpdir_prefix = os.path.join(tempfile.gettempdir(), 'produce-and-publish')
        if not os.path.exists(tmpdir_prefix):
            os.makedirs(tmpdir_prefix)
        destdir = tempfile.mkdtemp(dir=tmpdir_prefix, prefix=self.context.getId() + '-')

        # debug/logging
        params = kw.copy()
        params.update(self.request.form)
        LOG.info('new job (%s, %s) - outdir: %s' % (args, params, destdir))

        # get hold of the language (hyphenation support)
        language = getLanguageForObject(self.context)
        if params.get('language'):
            language = params.get('language')

        # call the dedicated @@asHTML on the top-level node. For a leaf document
        # this will return either a HTML fragment for a single document or @@asHTML
        # might be defined as an aggregator for a bunch of documents (e.g. if the
        # top-level is a folderish object
        html_view = self.context.restrictedTraverse('@@asHTML', None)
        if not html_view:
            raise RuntimeError('Object at does not provide @@asHTML view (%s, %s)' % 
                               (self.context.absolute_url(1), self.context.portal_type))
        html_fragment = html_view()

        # arbitrary application data
        data = params.get('data', None)

        template_id = params.get('template', 'pdf_template.pt')
        if not self.resource.fslayer.exists(template_id):
            raise IOError('Resource does not contain template file {}'.format(template_id))
        template = PageTemplate()
        with self.resource.fslayer.open(template_id, 'rb') as fp:
            template.write(fp.read())

        # copy resource files
        self.copyResourceFiles(destdir)

        # Now render the complete HTML document
        html = template(self,
                        context=self.context,
                        request=self.request,
                        language=language,
                        body=html_fragment,
                        data=data,
                        )

        # and apply transformations
        html = self.transformHtml(html, destdir)

        # and store it in a dedicated working directory
        dest_filename = os.path.join(destdir, 'index.html')
        with codecs.open(dest_filename, 'wb', encoding='utf-8') as fp:
            fp.write(html)

        # create a local ZIP file containing all the data for the conversion
        # basically for debugging purposes only.
        if ZIP_OUTPUT or 'zip_output' in params:
            archivename = tempfile.mktemp(suffix='.zip')
            fp = zipfile.ZipFile(archivename, "w", zipfile.ZIP_DEFLATED) 
            for root, dirs, files in os.walk(destdir):
                for fn in files:
                    absfn = os.path.join(root, fn)
                    zfn = absfn[len(destdir)+len(os.sep):] #XXX: relative path
                    fp.write(absfn, zfn)
            fp.close()
            LOG.info('ZIP file written to %s' % archivename)

        if 'no_conversion' in params:
            return destdir

        converter = params.get('converter', DEFAULT_CONVERTER)
        
        # Produce & Publish server integration
        from pp.client.python import pdf
        result = pdf.pdf(destdir, converter, server_url=SERVER_URL)
        output_filename = result['output_filename']
        LOG.info('Output file: %s' % output_filename)
        return output_filename

InitializeClass(ProducePublishView)


class PDFDownloadView(ProducePublishView):

    def __call__(self, *args, **kw):
        output_file = super(PDFDownloadView, self).__call__(*args, **kw)
        mimetype = os.path.splitext(os.path.basename(output_file))[1]
        R = self.request.response
        R.setHeader('content-type', 'application/%s' % mimetype)
        R.setHeader('content-disposition', 'attachment; filename="%s.%s"' % (self.context.getId(), mimetype))
        R.setHeader('pragma', 'no-cache')
        R.setHeader('cache-control', 'no-cache')
        R.setHeader('Expires', 'Fri, 30 Oct 1998 14:19:41 GMT')
        R.setHeader('content-length', os.path.getsize(output_file))
        return filestream_iterator(output_file, 'rb').read()

InitializeClass(PDFDownloadView)

