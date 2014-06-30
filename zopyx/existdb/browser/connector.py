################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import re
import fs
import fs.errors
import fs.path
import hurry.filesize
import urllib
import zipfile
import tempfile
import mimetypes
import logging
import zExceptions
from fs.opener import opener
from fs.contrib.davfs import DAVFS
from fs.zipfs import ZipFS
from zope.interface import implements
from zope.interface import implementer
from zope.component import getUtility
from zope.publisher.interfaces import IPublishTraverse
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.registry.interfaces import IRegistry
from plone.app.layout.globals.interfaces import IViewView
from zopyx.existdb.interfaces import IExistDBSettings
from zopyx.existdb.i18n import MessageFactory as _

from view_registry import precondition_registry
from view_registry import Precondition

import connector_views  # needed to initalize the registry
import config

LOG = logging.getLogger('zopyx.existdb')


@implementer(IPublishTraverse)
class Connector(BrowserView):

    view_name = 'view'
    template = ViewPageTemplateFile('connector_view.pt')

    implements(IViewView)

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.subpath = []

    def get_handle(self):
        """ Browser view method for returning the webdav handle """
        return self.fs_handle

    @property
    def fs_handle(self):

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IExistDBSettings)

        url = '{}/exist/webdav/db'.format(settings.existdb_url)

        if self.context.existdb_subpath:
            url += '/{}'.format(self.context.existdb_subpath)
        if self.subpath:
            url += '/{}'.format(urllib.quote('/'.join(self.subpath)))

        try:
            return DAVFS(url, credentials=dict(username=settings.existdb_username,
                                                 password=settings.existdb_password))
        except fs.errors.ResourceNotFoundError:
            msg = 'eXist-db path {} does not exist'.format(url)
            self.context.plone_utils.addPortalMessage(msg, 'error')
            LOG.error(msg)
            raise zExceptions.NotFound()
        except fs.errors.PermissionDeniedError:
            msg = 'eXist-db path {} unauthorizd access (check credentials)'.format(url)
            self.context.plone_utils.addPortalMessage(msg, 'error')
            LOG.error(msg)
            raise zExceptions.Unauthorized()

    @property
    def fs_handle_parent(self):

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IExistDBSettings)

        url = '{}/exist/webdav/db'.format(settings.existdb_url)

        if self.context.existdb_subpath:
            url += '/{}'.format(self.context.existdb_subpath)
        if self.subpath:
            url += '/{}'.format(urllib.quote('/'.join(self.subpath[:-1])))

        try:
            return DAVFS(url, credentials=dict(username=settings.existdb_username,
                                                 password=settings.existdb_password))
        except fs.errors.ResourceNotFoundError:
            msg = 'eXist-db path {} does not exist'.format(url)
            self.context.plone_utils.addPortalMessage(msg, 'error')
            LOG.error(msg)
            raise zExceptions.NotFound()
        except fs.errors.PermissionDeniedError:
            msg = 'eXist-db path {} unauthorizd access (check credentials)'.format(url)
            self.context.plone_utils.addPortalMessage(msg, 'error')
            LOG.error(msg)
            raise zExceptions.Unauthorized()

    def redirect(self, message=None, level='info'):
        if message:
            self.context.plone_utils.addPortalMessage(message, level)
        return self.request.response.redirect(self.context.absolute_url())


    def __call__(self, *args, **kw):

        handle = self.fs_handle
        if handle.isdir('.'):
            files = handle.listdirinfo(files_only=True)
            files = [f for f in files if not f[0].startswith('.')]
            files = sorted(files)
            dirs = handle.listdirinfo(dirs_only=True)
            dirs = sorted(dirs)
            dirs = [d for d in dirs if not d[0].startswith('.')]
            return self.template(
                    subpath='/'.join(self.subpath),
                    files=files, 
                    dirs=dirs)

        elif handle.isfile('.'):
            filename = self.subpath[-1]
            self.request.subpath = self.subpath
            self.request.context = self.context
            return precondition_registry.dispatch(handle, filename, self.view_name, self.request)

        else:
            raise RuntimeError()

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    def is_ace_editable(self, name):
        """ check if the given filename is editable using ACE editor """
        mt, encoding = mimetypes.guess_type(name)
        return mt in config.ACE_MODES

    def human_readable_filesize(self, num_bytes):
        """ Return num_bytes as human readable representation """
        return hurry.filesize.size(num_bytes, hurry.filesize.alternative)

    def searchabletext(self):
        """ Return indexable content """
        handle = self.fs_handle
        if 'index.html' in handle.listdir():
            with handle.open('index.html', 'rb') as fp:
                return fp.read()
        return None

    def reindex(self):
        """ Reindex current connector """
        self.context.reindexObject()
        self.context.log('Reindexed')
        return self.redirect(u'Reindex successfully')

    def datetime2DateTime(self, dt):
        """ Convert Python datetime.datetime to Zope DateTime.DateTime """
        view = self.context.restrictedTraverse('@@plone').toLocalizedTime
        return view(dt, True)

    def clear_contents(self):
        """ Remove all sub content """

        handle = self.fs_handle
        for name in handle.listdir():
            if handle.isfile(name):
                handle.remove(name)
            else:
                handle.removedir(name, force=True, recursive=False)

        return self.redirect(_(u'eXist-db collection cleared'))

    def zip_export(self, download=True):
        """ Export WebDAV subfolder to a ZIP file """

        handle = self.fs_handle

        zip_filename = tempfile.mktemp(suffix='.zip')
        zf = zipfile.ZipFile(zip_filename, 'w')
        for dirname, filenames in handle.walk():
            if dirname.startswith('/'):
                dirname = dirname.lstrip('/')
            for filename in filenames:
                z_filename = fs.path.join(dirname, filename)
                with handle.open(z_filename, 'rb') as fp:
                    zf.writestr(z_filename, fp.read())
        zf.close()

        if download:
            self.request.response.setHeader('content-type', 'application/zip')
            self.request.response.setHeader('content-size', os.path.getsize(zip_filename))
            self.request.response.setHeader('content-disposition', 'attachment; filename={}.zip'.format(self.context.id))
            with open(zip_filename, 'rb') as fp:
                self.request.response.write(fp.read())
            os.unlink(zip_filename)
            return
        else:
            return zip_filename
        

    def zip_import(self, zip_file=None, clean_directories=[]):
        """ Import WebDAV subfolder from an uploaded ZIP file """

        handle = self.fs_handle

        if not zip_file:
            zip_filename = self.request.zipfile.filename
            zip_file = self.request.zipfile
        else:
            zip_filename = zip_file
            zip_file = open(zip_file, 'rb')
            LOG.info('ZIP import ({})'.format(zip_filename))
        
        with ZipFS(zip_file, 'r') as zip_handle:
            # Cleanup webdav directory first
            for name in handle.listdir():
                if not name in clean_directories:
                    continue
                if handle.isfile(name):
                    handle.remove(name)
                else:
                    handle.removedir(name, force=True, recursive=False)
            self.context.log(u'Subdirectory cleared (ZIP import)')

            # import all files from ZIP into WebDAV
            count = 0
            for name in zip_handle.walkfiles():
                dirname = '/'.join(name.split('/')[:-1])
                try:
                    handle.makedir(dirname, recursive=True, allow_recreate=True)
                except Exception as e:
                    LOG.error('Failed creating {} failed ({})'.format(dirname, e))
               
                LOG.info('ZIP filename({})'.format(name))
                out_fp = handle.open(name.lstrip('/'), 'wb') 
                zip_fp = zip_handle.open(name, 'rb')
                out_fp.write(zip_fp.read())
                count += 1
#                out_fp.close()
#                zip_fp.close()

        self.context.log(u'ZIP file imported ({}, {} files)'.format(zip_filename, count))
        return self.redirect(_(u'Uploaded ZIP archive imported'))


class AceEditor(Connector):
    view_name = 'view-editor'

    def __call__(self, *args, **kw):
        method = self.request.method
        if method == 'GET':
            return super(AceEditor, self).__call__(*args, **kw)
        elif method == 'POST':
            handle = self.fs_handle_parent
            with handle.open(self.subpath[-1], 'wb') as fp:
                fp.write(self.request.data)
            return 'done'


class AceEditorReadonly(Connector):
    view_name = 'view-editor-readonly'


class Logging(BrowserView):

    template = ViewPageTemplateFile('connector_log.pt')

    def __call__(self):
        return self.template()
