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
import tempfile
import mimetypes
import logging
import unicodedata
import zExceptions
from dateutil import tz
from fs.zipfs import ZipFS
from progressbar import Bar, ETA, Percentage, ProgressBar, RotatingMarker
from zope.interface import implements
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
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

        # request/force_default_view can be used to force a redirect to the
        # default anonymous view
        force_default_view = self.request.form.get('force_default_view', 0)
        if force_default_view:
            if user.has_permission(permissions.View, self.context):
                default_view = self.context.default_view_anonymous
                return self.request.response.redirect(
                    '{}/{}'.format(self.context.absolute_url(), default_view))
            else:
                LOG.error(u'Unable to redirect to anonymous default view of ({}, {})'.format(
                    user.getUserName(),
                    self.context.absolute_url(1)))
                raise zExceptions.NotFound()

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
            LOG.debug(msg)
            raise zExceptions.NotFound()
        except fs.errors.PermissionDeniedError as e:
            msg = 'eXist-db path {} unauthorized access (check credentials)'.format(
                e.url)
            self.context.plone_utils.addPortalMessage(msg, 'error')
            LOG.error(msg)
            raise zExceptions.Unauthorized()

    def webdav_handle_root(self):
        return self.webdav_handle(root=True)

    def redirect(self, message=None, level='info', subpath=None):
        if message:
            self.context.plone_utils.addPortalMessage(message, level)
        url = self.context.absolute_url()
        if subpath:
            if isinstance(subpath, unicode):
                subpath = subpath.encode('utf8')
            url = '{}/@@view/{}'.format(url, subpath)
        return self.request.response.redirect(url)

    def __call__(self, *args, **kw):

        handle = self.webdav_handle()

        if handle.isdir('.'):

            context_url = self.context.absolute_url()
            view_prefix = '@@view'
            edit_prefix = '@@view-editor'
            remove_prefix = '@@remove-from-collection?subpath='
            if self.subpath:
                view_prefix += '/' + '/'.join(self.subpath)
                edit_prefix += '/' + '/'.join(self.subpath)
                remove_prefix += '/' + '/'.join(self.subpath)

            files = list()
            for info in handle.listdirinfo(files_only=True):
                if not info[0].startswith('.'):
                    try:
                        size = self.human_readable_filesize(info[1]['size'])
                    except KeyError:
                        size = u'n/a'
                    files.append(dict(url='{}/{}/{}'.format(context_url, view_prefix, info[0]),
                                      remove_url='{}/{}&name={}'.format(
                                          context_url, remove_prefix, info[0]),
                                      edit_url='{}/{}/{}'.format(
                                          context_url, edit_prefix, info[0]),
                                      title=info[0],
                                      editable=self.is_ace_editable(info[0]),
                                      st_mode=info[1]['st_mode'],
                                      size_original=info[1]['size'],
                                      size=size,
                                      modified_original=info[1]['modified_time'],
                                      modified=self.human_readable_datetime(info[1]['modified_time'])))

            dirs = list()
            for info in handle.listdirinfo(dirs_only=True):
                url = '{}/{}/{}'.format(context_url, view_prefix, info[0].encode('utf8'))
                dirs.append(dict(url=url,
                                 title=info[0],
                                 st_mode=info[1]['st_mode'],
                                 modified_original=info[1]['modified_time'],
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

        if not name:
            raise ValueError(_(u'No "name" given'))

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

    def remove_from_collection(self, subpath, name):
        """ Remove a collection """

        handle = self.webdav_handle(subpath)
        if handle.exists(name):
            handle.remove(name)
            msg = u'Removed {}'.format(name)
            self.logger.log(msg)
            self.context.plone_utils.addPortalMessage(msg)
        else:

            self.request.response.setStatus(404)
            return 'not found'
        return self.request.response.redirect(
            '{}/@@view/{}'.format(self.context.absolute_url(), subpath))

    def rename_collection(self, subpath, name, new_name):
        """ Rename a collection """

        if not new_name:
            raise ValueError(_(u'No new "name" given'))

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

    def zip_export(self, download=True, dirs=None, subpath=u''):
        """ Export WebDAV subfolder to a ZIP file.
            ``dirs`` optional comma separated list of top-level
            directory names to be exported.
        """

        if dirs:
            dirs = dirs.split(',')

        if not isinstance(subpath, unicode):
            subpath = unicode(subpath, 'utf8')

        handle = self.webdav_handle()
        zip_filename = tempfile.mktemp(suffix='.zip')
        with ZipFS(zip_filename, 'w', encoding='utf8') as zip_fs:
            for dirname, filenames in handle.walk(subpath):
                if dirname.startswith('/'):
                    dirname = dirname.lstrip('/')
                if dirs:
                    dir_paths = dirname.split('/')
                    if dir_paths[0] not in dirs:
                        continue
                for filename in filenames:
                    z_filename = fs.path.join(dirname, filename)
                    with handle.open(z_filename, 'rb') as fp:
                        with zip_fs.open(z_filename, 'wb') as zip_out:
                            zip_out.write(fp.read())

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

    def zip_import_ui(self, zip_file=None, subpath=None, clean_directories=None):
        """ Import WebDAV subfolder from an uploaded ZIP file """

        try:
            imported_files = self.zip_import(zip_file, subpath, clean_directories)
        except Exception as e:
            msg = u'ZIP import failed'
            LOG.error(msg, exc_info=True)
            return self.redirect(msg, 'error')

        self.logger.log(
            'ZIP file imported ({}, {} files)'.format(zip_file, len(imported_files)), details=imported_files)
        return self.redirect(_(u'Uploaded ZIP archive imported'), subpath=subpath)

    def zip_import(self, zip_file=None, subpath=None, clean_directories=None):
        """ Import WebDAV subfolder from an uploaded ZIP file """

        if subpath and not isinstance(subpath, unicode):
            subpath = unicode(subpath, 'utf8')

        if clean_directories is None:
            clean_directories = []

        handle = self.webdav_handle()

        if not zip_file:
            zip_filename = self.request.zipfile.filename
            zip_file = self.request.zipfile
        else:
            zip_filename = zip_file
            zip_file = open(zip_file, 'rb')
            LOG.info('ZIP import ({})'.format(zip_filename))

        imported_files = list()

        # zip_import() can also be used to upload single files
        # into the current webdav folder
        if not zip_filename.endswith('.zip'):
            if subpath:
                target_filename = '{}/{}'.format(subpath, zip_filename)
            else:
                target_filename = zip_filename
            if not target_filename:
                raise ValueError(u'No filename detected, did you really upload a file?')
            with handle.open(target_filename, 'wb') as fp:
                fp.write(zip_file.read())

            imported_files.append(target_filename)
            msg = u'File "{}" imported'.format(zip_filename)
            self.logger.log(msg)
            return imported_files

        try:
            with ZipFS(zip_file, 'r', encoding='utf-8') as zip_handle:
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

                show_progress = not os.environ.get('TESTING')
                if show_progress:
                    pbar = ProgressBar(
                        widgets=widgets, maxval=len(files)).start()

                # import all files from ZIP into WebDAV
                count = 0
                dirs_created = set()
                for i, name in enumerate(zip_handle.walkfiles()):
                    if show_progress:
                        pbar.update(i)

                    target_filename = unicodedata.normalize('NFC', name).lstrip('/')
                    if subpath:
                        target_filename = u'{}/{}'.format(subpath, target_filename)

                    target_dirname = '/'.join(target_filename.split('/')[:-1])
                    if target_dirname not in dirs_created:
                        try:
                            handle.makedir(
                                target_dirname, recursive=True, allow_recreate=True)
                            dirs_created.add(target_dirname)
                        except Exception as e:
                            LOG.error(
                                'Failed creating {} failed ({})'.format(target_dirname, e))

                    LOG.info(u'ZIP filename({})'.format(name))

                    out_fp = handle.open(target_filename, 'wb')
                    zip_fp = zip_handle.open(name, 'rb')
                    out_fp.write(zip_fp.read())
                    out_fp.close()
                    imported_files.append(target_filename)
                    count += 1

                zip_fp.close()
                if show_progress:
                    pbar.finish()

        except fs.zipfs.ZipOpenError as e:
            msg = u'Error opening ZIP file: {}'.format(e)
            raise RuntimeError(msg)
        return imported_files


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
