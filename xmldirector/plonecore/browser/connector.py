# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import fs
import stat
import json
import datetime
import fs.errors
import itertools
import fs.path
import humanize
import operator
import hurry.filesize
import tempfile
import mimetypes
import unicodedata
import logging
import pkg_resources
from dateutil import tz
from fs.zipfs import ZipFS
from progressbar import Bar, ETA, Percentage, ProgressBar, RotatingMarker

import zExceptions
from zope.interface import implements
from zope.interface import implementer
from zope.interface import alsoProvides
from zope.publisher.interfaces import IPublishTraverse
from plone.app.layout.globals.interfaces import IViewView
from plone.protect.interfaces import IDisableCSRFProtection
from AccessControl.SecurityManagement import getSecurityManager
from ZPublisher.Iterators import IStreamIterator
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from xmldirector.plonecore.i18n import MessageFactory as _
from zopyx.plone.persistentlogger.logger import IPersistentLogger

from .view_registry import precondition_registry
from . import connector_views  # NOQA - needed to initalize the registry
from . import config

LOG = logging.getLogger('xmldirector.plonecore')

TZ = os.environ.get('TZ', 'UTC')
LOG.debug('Local timezone: {}'.format(TZ))


def stmode2unix(st_mode):
    if st_mode:
        is_dir = 'd' if stat.S_ISDIR(st_mode) else '-'
        dic = {'7': 'rwx', '6': 'rw-', '5': 'r-x', '4': 'r--', '0': '---'}
        perm = str(oct(st_mode)[-3:])
        return is_dir + ''.join(dic.get(x, x) for x in perm)
    else:
        return u''


def safe_unicode(s):
    if not isinstance(s, unicode):
        return unicode(s, 'utf8')
    return s


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


class connector_iterator(file):
    """ Iterator for pyfilesystem content """

    implements(IStreamIterator)

    def __init__(self, handle, filename, mode='rb', streamsize=1 << 16):
        self.fp = handle.open(filename, mode)
        self.streamsize = streamsize

    def next(self):
        data = self.fp.read(self.streamsize)
        if not data:
            raise StopIteration
        return data

    def __len__(self):
        cur_pos = self.fp.tell()
        self.fp.seek(0, 2)
        size = self.fp.tell()
        self.seek(cur_pos, 0)
        return size


class Dispatcher(BrowserView):

    def __call__(self, *args, **kw):

        qs = self.request.QUERY_STRING
        user = getSecurityManager().getUser()

        # request/force_default_view can be used to force a redirect to the
        # default anonymous view
        force_default_view = self.request.form.get('force_default_view', 0)
        if force_default_view:
            if user.has_permission(permissions.View, self.context):
                default_view = self.context.default_view_anonymous
                if qs:
                    default_view += '?' + qs
                return self.request.response.redirect(
                    '{}/{}'.format(self.context.absolute_url(), default_view))
            else:
                LOG.error(u'Unable to redirect to anonymous default view of ({}, {})'.format(
                    user.getUserName(),
                    self.context.absolute_url(1)))
                raise zExceptions.NotFound()

        if user.has_permission(permissions.ModifyPortalContent, self.context):
            default_view = self.context.default_view_authenticated
            if qs:
                default_view += '?' + qs
            return self.request.response.redirect(
                '{}/{}'.format(self.context.absolute_url(), default_view))
        else:
            default_view = self.context.default_view_anonymous
            if default_view:
                if qs:
                    default_view += '?' + qs
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
        self.filter_by = request.get('filter_by', '')
        self.traversal_subpath = []

    def is_plone5(self):
        version = pkg_resources.get_distribution('Products.CMFPlone').version
        return version.startswith('5')

    def __bobo_traverse__(self, request, entryname):
        """ Traversal hook for (un)restrictedTraverse() """
        self.traversal_subpath.append(entryname)
        traversal_subpath = '/'.join(self.traversal_subpath)
        handle = self.get_handle()
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

    def get_handle(self, subpath=None, root=False):
        """ Returns a webdav handle for the current subpath """

        if not root:
            if not subpath:
                subpath = '/'.join(self.subpath)

        try:
            return self.context.get_handle(subpath)
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

    def get_handle_root(self):
        return self.get_handle(root=True)

    def redirect(self, message=None, level='info', subpath=None):
        if message:
            self.context.plone_utils.addPortalMessage(message, level)
        url = self.context.absolute_url()
        if subpath:
            if isinstance(subpath, unicode):
                subpath = subpath.encode('utf8')
            url = '{}/@@view/{}'.format(url, subpath)
        return self.request.response.redirect(url)

    def folder_contents(self, subpath='', filter_by=None):
        """ AJAX callback """

        handle = self.get_handle(subpath)
        context_url = self.context.absolute_url()
        view_prefix = u'@@view'
        edit_prefix = u'@@view-editor'
        remove_prefix = u'@@remove-from-collection?subpath='
        joined_subpath = u'{}'.format(safe_unicode(subpath))
        parent_subpath = ''
        if subpath:
            parent_subpath = u'/'.join(joined_subpath.split('/')[:-1])

        if subpath:
            view_prefix += u'/{}'.format(joined_subpath)
            edit_prefix += u'/{}'.format(joined_subpath)
            remove_prefix += u'/{}'.format(joined_subpath)

        files = list()
        for info in handle.listdirinfo(files_only=True):
            path_name = safe_unicode(info[0])
            fullpath = u'{}/{}'.format(joined_subpath, path_name)
            if not path_name.startswith('.'):
                try:
                    size = self.human_readable_filesize(info[1]['size'])
                except KeyError:
                    size = u'n/a'

                modified = None
                modified_original = info[1].get('modified_time')
                if modified_original:
                    modified = self.human_readable_datetime(
                        info[1]['modified_time'], to_utc=False)

                basename, ext = os.path.splitext(path_name)
                ext = ext.lower().lstrip('.')
                files.append(dict(url=u'{}/{}/{}'.format(context_url, view_prefix, path_name),
                                  type='file',
                                  fullpath=fullpath,
                                  remove_url=u'{}/{}&name={}'.format(
                                      context_url, remove_prefix, path_name),
                                  edit_url=u'{}/{}/{}'.format(
                                      context_url, edit_prefix, path_name),
                                  title=info[0],
                                  ext=ext,
                                  editable=self.is_ace_editable(path_name),
                                  st_mode=info[1].get('st_mode'),
                                  st_mode_text=stmode2unix(
                                      info[1].get('st_mode')),
                                  size_original=info[1].get('size'),
                                  size=size,
                                  modified_original=modified_original,
                                  modified=modified))

        dirs = []
        if subpath:
            dirs.append(dict(
                type=u'directory',
                title='..',
                fullpath=parent_subpath,
                url=u'{}/@@view/{}'.format(self.context.absolute_url(),
                                           parent_subpath)
            ))
        for info in handle.listdirinfo(dirs_only=True):
            path_name = safe_unicode(info[0])
            fullpath = u'{}/{}'.format(joined_subpath, path_name)
            url = u'{}/{}/{}'.format(context_url, view_prefix, path_name)
            modified = info[1].get('modified_time')
            dirs.append(dict(url=url,
                             fullpath=fullpath,
                             type='directory',
                             ext=u'',
                             title=path_name,
                             st_mode=info[1].get('st_mode'),
                             st_mode_text=stmode2unix(info[1].get('st_mode')),
                             modified_original=modified,
                             modified=self.human_readable_datetime(modified), to_utc=False))

        index = itertools.count()
        dirs = sorted(dirs, key=operator.itemgetter('title'))
        [d.update(index=index.next()) for d in dirs]
        files = sorted(files, key=operator.itemgetter('title'))
        [f.update(index=index.next()) for f in files]
        result = dict(dirs=dirs, files=files)
        self.request.response.setHeader('Pragma', 'no-cache')
        self.request.response.setHeader('Cache-control', 'no-store')
        return json.dumps(result, default=json_serial)

    def _subpath_components(self):

        result = []
        for count, item in enumerate(self.subpath):
            href = '{}/@@view/{}'.format(self.context.absolute_url(), '/'.join(self.subpath[:count+1]))
            result.append(dict(href=href, title=item))            
        return result

    def __call__(self, *args, **kw):

        handle = self.get_handle()
        if handle.isDirectory():
            return self.template(
                filter_by=self.filter_by,
                subpath_components=self._subpath_components(),
                subpath='/'.join(self.subpath))
        elif handle.isFile():
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

    def human_readable_datetime(self, dt=None, to_utc=False):
        """ Convert with `dt` datetime string into a human readable
            representation using humanize module.
        """
        if dt:
            if to_utc:
                diff = datetime.datetime.utcnow() - dt
                return humanize.naturaltime(diff)
            else:
                return humanize.naturaltime(dt)

    def upload_file(self):
        """ AJAX callback for Uploadify """

        alsoProvides(self.request, IDisableCSRFProtection)

        subpath = self.request.get('subpath')
        get_handle = self.context.get_handle(subpath=subpath)
        filename = os.path.basename(self.request.file.filename)
        basename, ext = os.path.splitext(filename)

        with get_handle.open(filename, 'wb') as fp:
            self.request.file.seek(0)
            data = self.request.file.read()
            fp.write(data)

        self.logger.log(
            u'{} uploaded ({} Byte)'.format(repr(filename), len(data)))
        self.request.response.setStatus(200)
        self.request.response.write('OK')

    def zip_import_ui(self, zip_file=None, subpath=None, clean_directories=None):
        """ Import WebDAV subfolder from an uploaded ZIP file """

        try:
            imported_files = self.zip_import(
                zip_file, subpath, clean_directories)
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

        handle = self.get_handle()

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
                raise ValueError(
                    u'No filename detected, did you really upload a file?')
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

                    target_filename = unicodedata.normalize(
                        'NFC', name).lstrip('/')
                    if subpath:
                        target_filename = u'{}/{}'.format(
                            subpath, target_filename)

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

    def filemanager_rename(self, subpath, old_id, new_id):
        """ Rename folder or file ``old_id`` inside directory ``subpath`` to ``new_id`` """

        alsoProvides(self.request, IDisableCSRFProtection)
        handle = self.get_handle(subpath)

        subpath = handle.convert_string(subpath)
        old_id = handle.convert_string(old_id)
        new_id = handle.convert_string(new_id)

        if not handle.exists(old_id):
            msg = handle.convert_string(
                u'{}/{} not found').format(subpath, old_id)
            raise zExceptions.NotFound(msg)

        if handle.exists(new_id):
            msg = handle.convert_string(
                u'{}/{} already exists').format(subpath, new_id)
            self.request.response.setStatus(500)
            return msg

        try:
            handle.rename(old_id, new_id)
        except Exception as e:
            msg = handle.convert_string(
                u'{}/{} could not be renamed to "{}/{}" ({})').format(subpath, old_id, subpath, new_id, str(e))
            self.request.response.setStatus(500)
            return msg

        msg = handle.convert_string(
            u'Renamed {}/{} to {}/{}').format(subpath, old_id, subpath, new_id)
        self.logger.log(msg)
        self.request.response.setStatus(200)
        return msg

    def filemanager_delete(self, subpath, id):
        """ Delete a folder or file ``id`` inside the folder ``subpath`` """

        alsoProvides(self.request, IDisableCSRFProtection)
        handle = self.get_handle(subpath)

        subpath = handle.convert_string(subpath)
        id = handle.convert_string(id)

        if not handle.exists(id):
            msg = handle.convert_string(u'{}/{} not found').format(subpath, id)
            raise zExceptions.NotFound(msg)

        if handle.isdir(id):
            try:
                handle.removedir(id, recursive=True, force=True)
            except Exception as e:
                msg = handle.convert_string(
                    u'{}/{} could not be deleted ({})').format(subpath, id, str(e))
                self.request.response.setStatus(500)
                return msg

        elif handle.isfile(id):

            try:
                handle.remove(id)
            except Exception as e:
                msg = handle.convert_string(
                    u'{}/{} could not be deleted ({})').format(subpath, id, str(e))
                self.request.response.setStatus(500)
                return msg

        else:
            raise RuntimeError(handle.convert_string(
                u'Unhandled file type {}/{}').format(subpath, id))

        msg = handle.convert_string(u'Deleted {}/{}').format(subpath, id)
        self.logger.log(msg)
        self.request.response.setStatus(200)
        return msg

    def filemanager_create_collection(self, subpath, new_id):
        """ Create a new collection ``new_id`` inside the folder ``subpath `` """

        alsoProvides(self.request, IDisableCSRFProtection)
        handle = self.get_handle(subpath)

        subpath = handle.convert_string(subpath)
        new_id = handle.convert_string(new_id)

        if handle.exists(new_id):
            msg = handle.convert_string(
                u'{}/{} already exists found').format(subpath, new_id)
            self.request.response.setStatus(500)
            return msg

        try:
            handle.makedir(new_id)
        except Exception as e:
            msg = handle.convert_string(
                u'{}/{} could not be created ({})').format(subpath, new_id, str(e))
            self.request.response.setStatus(500)
            return msg

        msg = handle.convert_string(u'Created {}/{}').format(subpath, new_id)
        self.logger.log(msg)
        self.request.response.setStatus(200)
        return msg

    def filemanager_zip_download(self, subpath, download=True, zip_max_size=100 * 1024 * 1024):
        """ Download all files of ``subpath`` as ZIP file """

        alsoProvides(self.request, IDisableCSRFProtection)

        handle = self.get_handle()
        subpath = handle.convert_string(subpath)
        if not handle.exists(subpath) or not handle.isdir(subpath):
            raise ValueError(handle.convert_string(
                u'{} does not exist or is not a directory').format(subpath))

        zip_filename = tempfile.mktemp(suffix='.zip')
        zip_size = 0
        with ZipFS(zip_filename, 'w', encoding='utf8') as zip_fs:
            for dirname, filenames in handle.walk(subpath):
                if dirname.startswith('/'):
                    dirname = dirname.lstrip('/')
                for filename in filenames:
                    local_filename = fs.path.join(dirname, filename)
                    z_filename = fs.path.join(dirname, filename)
                    z_filename = unicodedata.normalize(
                        'NFKD', z_filename).encode('ascii', 'ignore')
                    with handle.open(local_filename, 'rb') as fp:
                        with zip_fs.open(z_filename, 'wb') as zip_out:
                            data = fp.read()
                            zip_out.write(data)
                            zip_size += len(data)
                        if zip_size > zip_max_size:
                            raise RuntimeError(u'Too many files - ZIP file size exceeded ({})'.format(
                                self.human_readable_filesize(zip_max_size)))

        if download:
            download_filename = '{}-{}.zip'.format(
                self.context.getId(), os.path.basename(subpath))
            self.request.response.setHeader('content-type', 'application/zip')
            self.request.response.setHeader(
                'content-length', os.path.getsize(zip_filename))
            self.request.response.setHeader(
                'content-disposition', 'attachment; filename={}'.format(download_filename))
            with open(zip_filename, 'rb') as fp:
                self.request.response.write(fp.read())
            os.unlink(zip_filename)
            return
        else:
            return zip_filename

    def filemanager_download(self, filename):
        """ Download/stream the given file """

        handle = self.get_handle()
        filename = handle.convert_string(filename)
        if not handle.exists(filename):
            raise zExceptions.NotFound(handle.convert_string(
                u'{} does not exist').format(filename))
        basename = os.path.basename(filename)
        basename, ext = os.path.splitext(basename)
        mt, encoding = mimetypes.guess_type(basename)
        self.request.response.setHeader('content-type', 'mt')
        self.request.response.setHeader(
            'content-length', handle.getsize(filename))
        self.request.response.setHeader(
            'content-disposition', 'attachment; filename={}'.format(os.path.basename(filename)))
        return connector_iterator(handle, filename)


class AceEditor(Connector):
    view_name = 'view-editor'

    def __call__(self, *args, **kw):
        method = self.request.method
        if method == 'GET':
            return super(AceEditor, self).__call__(*args, **kw)
        elif method == 'POST':
            handle = self.get_handle_root()
            fp = handle.open('/'.join(self.subpath), 'wb')
            fp.write(self.request.data)
            # does not work ParentDirectoryMissingError: ParentDi...ngError()
            fp.close()
            return 'done'


class AceEditorReadonly(Connector):
    view_name = 'view-editor-readonly'


class Raw(Connector):

    def __call__(self, *args, **kw):

        resource = '/'.join(self.subpath)
        handle = self.context.get_handle()
        if not handle.exists(resource):
            raise zExceptions.NotFound(resource)
        mt, encoding = mimetypes.guess_type(resource)
        self.request.response.setHeader('content-type', mt)
        self.request.response.setHeader(
            'content-length', str(handle.getsize(resource)))
        with handle.open(resource, 'rb') as fp:
            self.request.response.write(fp.read())
