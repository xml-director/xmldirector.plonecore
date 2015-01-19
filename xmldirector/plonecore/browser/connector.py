# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import fs
import datetime
import fs.errors
import fs.path
import humanize
import operator
import hurry.filesize
import zipfile
import tempfile
import mimetypes
import logging
import zExceptions
from dateutil import tz
from fs.zipfs import ZipFS
from progressbar import Bar, ETA, Percentage, ProgressBar, RotatingMarker
from zope.interface import implements
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from App.config import getConfiguration
from AccessControl.SecurityManagement import getSecurityManager
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore import permissions
from plone.app.layout.globals.interfaces import IViewView
from xmldirector.plonecore.i18n import MessageFactory as _
from xmldirector.plonecore.logger import IPersistentLogger

from .view_registry import precondition_registry

from . import connector_views  # NOQA - needed to initalize the registry
from . import config

LOG = logging.getLogger('xmldirector.plonecore')

TZ = os.environ.get('TZ', 'UTC')
LOG.info('Local timezone: {}'.format(TZ))


class Dispatcher(BrowserView):

    def __call__(self, *args, **kw):

        user = getSecurityManager().getUser()
        if user.has_permission(permissions.ModifyPortalContent, self.context):
            default_view = self.context.default_view_authenticated
            return self.request.response.redirect(
                '{}/{}'.format(self.context.absolute_url(), default_view))
        else:
            default_view = self.context.default_view_anonymous
            if default_view:
                return self.request.response.redirect(
                    '{}/{}'.format(self.context.absolute_url(), default_view))
            else:
                msg = _(u'No default view configured for anonymous visitors')
                self.context.plone_utils.addPortalMessage(msg, 'error')
                raise zExceptions.NotFound()


@implementer(IPublishTraverse)
class Connector(BrowserView):

    view_name = 'view'
    template = ViewPageTemplateFile('connector_view.pt')

    implements(IViewView)

    def __init__(self, context, request):
        super(Connector, self).__init__(context, request)
        self.subpath = []
        self.traversal_subpath = []

    def __bobo_traverse__(self, request, entryname):
        """ Traversal hook for (un)restrictedTraverse() """
        self.traversal_subpath.append(entryname)
        traversal_subpath = '/'.join(self.traversal_subpath)
        handle = self.webdav_handle()
        if handle.exists(traversal_subpath):
            if handle.isdir(traversal_subpath):
                return self
            elif handle.isfile(traversal_subpath):
                data = handle.open(traversal_subpath, 'rb').read()
                self.wrapped_object = data
                self.wrapped_info = handle.getinfo(traversal_subpath)
                try:
                    self.wrapped_meta = handle.getmeta(traversal_subpath)
                except fs.errors.NoMetaError:
                    self.wrapped_meta = None
                return self
        raise zExceptions.NotFound('not found: {}'.format(entryname))

    @property
    def logger(self):
        return IPersistentLogger(self.context)

    def webdav_handle(self, subpath=None, root=False):
        """ Returns a webdav handle for the current subpath """

        if not root:
            if not subpath:
                subpath = '/'.join(self.subpath)

        try:
            return self.context.webdav_handle(subpath)
        except fs.errors.ResourceNotFoundError as e:
            msg = 'eXist-db path {} does not exist'.format(e.url)
            self.context.plone_utils.addPortalMessage(msg, 'error')
            LOG.error(msg)
            raise zExceptions.NotFound()
        except fs.errors.PermissionDeniedError as e:
            msg = 'eXist-db path {} unauthorized access (check credentials)'.format(
                e.url)
            self.context.plone_utils.addPortalMessage(msg, 'error')
            LOG.error(msg)
            raise zExceptions.Unauthorized()

    def webdav_handle_root(self):
        return self.webdav_handle(root=True)

    def redirect(self, message=None, level='info'):
        if message:
            self.context.plone_utils.addPortalMessage(message, level)
        return self.request.response.redirect(self.context.absolute_url())

    def __call__(self, *args, **kw):

        handle = self.webdav_handle()

        if handle.isdir('.'):

            context_url = self.context.absolute_url()
            view_prefix = '@@view'
            edit_prefix = '@@view-editor'
            if self.subpath:
                view_prefix += '/' + '/'.join(self.subpath)
                edit_prefix += '/' + '/'.join(self.subpath)

            files = list()
            for info in handle.listdirinfo(files_only=True):
                if not info[0].startswith('.'):
                    try:
                        size = self.human_readable_filesize(info[1]['size'])
                    except KeyError:
                        size = u'n/a'
                    files.append(dict(url='{}/{}/{}'.format(context_url, view_prefix, info[0]),
                                      edit_url='{}/{}/{}'.format(
                                          context_url, edit_prefix, info[0]),
                                      title=info[0],
                                      editable=self.is_ace_editable(info[0]),
                                      size=size,
                                      modified=self.human_readable_datetime(info[1]['modified_time'])))

            dirs = list()
            for info in handle.listdirinfo(dirs_only=True):
                url = u'{}/{}/{}'.format(context_url, view_prefix, info[0])
                dirs.append(dict(url=url,
                                 title=info[0],
                                 modified=self.human_readable_datetime(info[1]['modified_time'])))

            dirs = sorted(dirs, key=operator.itemgetter('title'))
            files = sorted(files, key=operator.itemgetter('title'))

            return self.template(
                view_prefix=view_prefix,
                subpath='/'.join(self.subpath),
                files=files,
                dirs=dirs)

        elif handle.isfile('.'):
            filename = self.subpath[-1]
            self.request.subpath = self.subpath
            self.request.context = self.context
            return precondition_registry.dispatch(
                handle, filename, self.view_name, self.request)
        else:
            raise RuntimeError('This should not happen :-)')

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

    def create_collection(self, subpath, name):
        """ Create a new collection """

        handle = self.webdav_handle(subpath)
        if handle.exists(name):
            msg = u'Collection already exists'
            self.context.plone_utils.addPortalMessage(msg, 'error')
        else:
            handle.makedir(name)
            msg = u'Collection created'
            self.logger.log('Created {} (subpath: {})'.format(name, subpath))
            self.context.plone_utils.addPortalMessage(msg)
        return self.request.response.redirect(
            '{}/@@view/{}'.format(self.context.absolute_url(), subpath))

    def remove_collection(self, subpath, name):
        """ Remove a collection """

        handle = self.webdav_handle(subpath)
        if handle.exists(name):
            handle.removedir(name, force=True)
            msg = u'Collection removed'
            self.logger.log('Removed {} (subpath: {})'.format(name, subpath))
            self.context.plone_utils.addPortalMessage(msg)
        else:
            msg = u'Collection does not exist'
            self.context.plone_utils.addPortalMessage(msg, 'error')
        return self.request.response.redirect(
            '{}/@@view/{}'.format(self.context.absolute_url(), subpath))

    def rename_collection(self, subpath, name, new_name):
        """ Rename a collection """

        handle = self.webdav_handle(subpath)
        if handle.exists(name):
            handle.rename(name, new_name)
            msg = u'Collection renamed'
            self.logger.log(
                'Renamed {}  to {} (subpath: {})'.format(name, new_name, subpath))
            self.context.plone_utils.addPortalMessage(msg)
        else:
            msg = u'Collection does not exist'
            self.context.plone_utils.addPortalMessage(msg, 'error')
        return self.request.response.redirect(
            '{}/@@view/{}'.format(self.context.absolute_url(), subpath))

    def reindex(self):
        """ Reindex curnrent connector """
        self.context.reindexObject()
        self.logger.log('Reindexed')
        return self.redirect(u'Reindexing successfully')

    def datetime_tz(self, dt):
        """ Convert Python UTC datetime.datetime to Zope DateTime.DateTime """
        to_tz = tz.gettz(TZ)
        dt = dt.replace(tzinfo=tz.gettz('UTC'))
        return dt.astimezone(to_tz).strftime('%d.%m.%Y %H:%M:%Sh')

    def human_readable_datetime(self, dt):
        """ Convert with `dt` datetime string into a human readable
            representation using humanize module.
        """
        diff = datetime.datetime.utcnow() - dt
        return humanize.naturaltime(diff)

    def clear_contents(self):
        """ Remove all sub content """

        handle = self.webdav_handle()
        for name in handle.listdir():
            if handle.isfile(name):
                handle.remove(name)
            else:
                handle.removedir(name, force=True, recursive=False)

        return self.redirect(_(u'eXist-db collection cleared'))

    def zip_export(self, download=True):
        """ Export WebDAV subfolder to a ZIP file """

        handle = self.webdav_handle()

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
            self.request.response.setHeader(
                'content-size', os.path.getsize(zip_filename))
            self.request.response.setHeader(
                'content-disposition', 'attachment; filename={}.zip'.format(self.context.id))
            with open(zip_filename, 'rb') as fp:
                self.request.response.write(fp.read())
            os.unlink(zip_filename)
            return
        else:
            return zip_filename

    def zip_import(self, zip_file=None, subpath=None, clean_directories=[]):
        """ Import WebDAV subfolder from an uploaded ZIP file """

        handle = self.webdav_handle()

        if not zip_file:
            zip_filename = self.request.zipfile.filename
            zip_file = self.request.zipfile
        else:
            zip_filename = zip_file
            zip_file = open(zip_file, 'rb')
            LOG.info('ZIP import ({})'.format(zip_filename))

        # zip_import() can also be used to upload single files
        # into the current webdav folder
        if not zip_filename.endswith('.zip'):
            if subpath:
                target_filename = '{}/{}'.format(subpath, zip_filename)
            else:
                target_filename = zip_filename
            with handle.open(target_filename, 'wb') as fp:
                fp.write(zip_file.read())

            msg = u'File "{}" imported'.format(zip_filename)
            self.logger.log(msg)
            return self.redirect(_(msg))

        try:
            with ZipFS(zip_file, 'r') as zip_handle:
                # Cleanup webdav directory first
                for i, name in enumerate(handle.listdir()):
                    if name not in clean_directories:
                        continue
                    if handle.isfile(name):
                        handle.remove(name)
                    else:
                        handle.removedir(name, force=True, recursive=False)
                self.logger.log(u'Subdirectory cleared (ZIP import)')

                # setup progressbar
                widgets = ['ZIP import: ', Percentage(), ' ', Bar(
                    marker=RotatingMarker()), ' ', ETA(), ' ']
                files = list(zip_handle.walkfiles())

                try:
                    getConfiguration().testinghome
                    show_progress = False
                except AttributeError:
                    show_progress = True

                if show_progress:
                    pbar = ProgressBar(
                        widgets=widgets, maxval=len(files)).start()

                # import all files from ZIP into WebDAV
                count = 0
                for i, name in enumerate(zip_handle.walkfiles()):
                    if show_progress:
                        pbar.update(i)

                    dirname = '/'.join(name.split('/')[:-1])

                    try:
                        handle.makedir(
                            dirname, recursive=True, allow_recreate=True)
                    except Exception as e:
                        LOG.error(
                            'Failed creating {} failed ({})'.format(dirname, e))

                    LOG.info('ZIP filename({})'.format(name))

                    out_fp = handle.open(name.lstrip('/'), 'wb')
                    zip_fp = zip_handle.open(name, 'rb')
                    out_fp.write(zip_fp.read())
                    out_fp.close()
                    count += 1

                zip_fp.close()
                if show_progress:
                    pbar.finish()

        except fs.zipfs.ZipOpenError as e:
            msg = u'Error opening ZIP file: {}'.format(e)
            return self.redirect(msg, 'error')

        self.logger.log(
            u'ZIP file imported ({}, {} files)'.format(zip_filename, count))
        return self.redirect(_(u'Uploaded ZIP archive imported'))


class AceEditor(Connector):
    view_name = 'view-editor'

    def __call__(self, *args, **kw):
        method = self.request.method
        if method == 'GET':
            return super(AceEditor, self).__call__(*args, **kw)
        elif method == 'POST':
            handle = self.webdav_handle_root()
            fp = handle.open('/'.join(self.subpath), 'wb')
            fp.write(self.request.data)
            # does not work ParentDirectoryMissingError: ParentDi...ngError()
            fp.close()
            return 'done'


class AceEditorReadonly(Connector):
    view_name = 'view-editor-readonly'


class Logging(BrowserView):

    template = ViewPageTemplateFile('connector_log.pt')

    def entries(self):
        return IPersistentLogger(self.context).entries

    def log_clear(self):
        """ Clear connector persistent log """
        IPersistentLogger(self.context).clear()
        msg = u'Log entries cleared'
        self.context.plone_utils.addPortalMessage(msg)
        return self.request.response.redirect(
            '{}/connector-log'.format(self.context.absolute_url()))

    def __call__(self):
        return self.template()
