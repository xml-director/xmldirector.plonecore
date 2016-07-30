# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import time
import urllib
from furl import furl
import unidecode

import fs.errors
from fs.osfs import OSFS
from fs.ftpfs import FTPFS
from fs import iotools
from fs.contrib.davfs import DAVFS
from collections import namedtuple

import plone.api
import zope.globalrequest
from zExceptions import NotFound
from zope.component import getUtility
from zope.annotation import IAnnotations
from plone.registry.interfaces import IRegistry

from xmldirector.plonecore.locking import LockManager
from xmldirector.plonecore.locking import FileIsLocked
from xmldirector.plonecore.locking import LockError
from xmldirector.plonecore.logger import LOG


try:
    import paramiko  # NOQA
    have_paramiko = True
except ImportError:
    have_paramiko = False


try:
    import boto  # NOQA
    have_boto = True
except ImportError:
    have_boto = False

try:
    import dropbox  # NOQA
    from xmldirector.dropbox.browser import dropbox_authentication
    from xmldirector.dropbox.interfaces import IDropboxSettings
    have_dropbox = True
except ImportError:
    have_dropbox = False

_marker = object

lockstate = namedtuple('lockstate', 'op, mode, lock_owner')

# LOCK MODES

EXCL = 'exclusive'
SHRD = 'shared'

_marker = object


LOCK_PERMISSION_MAP = dict([
    # open(..., 'r')
    (lockstate(op='open_r', mode=EXCL, lock_owner=True), True),
    (lockstate(op='open_r', mode=SHRD, lock_owner=True), True),
    (lockstate(op='open_r', mode=EXCL, lock_owner=False), False),
    (lockstate(op='open_r', mode=SHRD, lock_owner=False), True),

    # open(..., 'w')
    (lockstate(op='open_w', mode=EXCL, lock_owner=True), True),
    (lockstate(op='open_w', mode=SHRD, lock_owner=True), True),
    (lockstate(op='open_w', mode=EXCL, lock_owner=False), False),
    (lockstate(op='open_w', mode=SHRD, lock_owner=False), False),

    # remove()
    (lockstate(op='remove', mode=EXCL, lock_owner=True), True),
    (lockstate(op='remove', mode=SHRD, lock_owner=True), True),
    (lockstate(op='remove', mode=EXCL, lock_owner=False), False),
    (lockstate(op='remove', mode=SHRD, lock_owner=False), False),

    # remove()
    (lockstate(op='move', mode=EXCL, lock_owner=True), True),
    (lockstate(op='move', mode=SHRD, lock_owner=True), True),
    (lockstate(op='move', mode=EXCL, lock_owner=False), False),
    (lockstate(op='move', mode=SHRD, lock_owner=False), False),

    # copy()
    (lockstate(op='copy', mode=EXCL, lock_owner=True), True),
    (lockstate(op='copy', mode=SHRD, lock_owner=True), True),
    (lockstate(op='copy', mode=EXCL, lock_owner=False), False),
    (lockstate(op='copy', mode=SHRD, lock_owner=False), True),
])


class RequiresAuthorizationError(RuntimeError):
    """ Exception for unauthorized request against service using OAuth """

    def __init__(self, msg, authorization_url):
        super(RequiresAuthorizationError, self).__init__(msg)
        self.authorization_url = authorization_url



class BaseWrapper(object):
    """ A wapper for DAVFS """

    supports_locks = True

    def isDirectory(self):
        """ Represents a directory """
        __leaf__ = getattr(self, '__leaf__', _marker)
        if __leaf__ != _marker:
            return not getattr(self, '__leaf__', False)
        if have_paramiko and isinstance(self, SFTPFSWrapper):
            return not self.isfile('.')
        return self.isdir('.')

    def isFile(self):
        """ Represents a file """
        __leaf__ = getattr(self, '__leaf__', _marker)
        if __leaf__ != _marker:
            return getattr(self, '__leaf__', False)
        if have_paramiko and isinstance(self, SFTPFSWrapper):
            return self.isfile('.')
        return self.isfile('.')

    @property
    def leaf_filename(self):
        __leaf__ = getattr(self, '__leaf__', _marker)
        if __leaf__ != _marker:
            # hack for OSFS, fix this
            return urllib.unquote(self.__leaf_filename__)
        if have_paramiko and isinstance(self, SFTPFSWrapper):
            return '.'
        if self.isFile():
            return '.'
        return '.'

    def _check_lock(self, path, op):

        if not self.supports_locks:
            return True

        # flag set by tests in order to avoid false posititves
        ignore_errors = getattr(self, 'ignore_errors', False)

        try:
            context = zope.globalrequest.getRequest().PUBLISHED.context
            lm = LockManager(context)
        except AttributeError:
            lm = LockManager(None)

        try:
            log_info = lm.get_lock(path)
        except LockError:
            return

        owner = log_info['owner']
        lock_mode = log_info['mode']
        lock_owner = (owner == plone.api.user.get_current().getUserName())
        allowed = LOCK_PERMISSION_MAP.get(
            lockstate(mode=lock_mode, op=op, lock_owner=lock_owner), _marker)
        msg = '(lock_mode={}, op={}, lock_owner={}'.format(
            lock_mode, op, lock_owner)
        if allowed is _marker and not ignore_errors:
            raise ValueError('No entry found for ({})'.format(msg))
        if not allowed and not ignore_errors:
            raise FileIsLocked('File is locked ({})'.format(msg))

    @iotools.filelike_to_stream
    def open(self, path, mode="r", lock_check=True, **kwargs):
        if lock_check:
            self._check_lock(path, op='open_{}'.format(mode[0]))
        for i in range(4):
            try:
                return super(BaseWrapper, self).open(path, mode, **kwargs)
            except fs.errors.OperationFailedError:
                time.sleep(1 + 2 * i)
        raise fs.errors.OperationFailedError(
            'Unable to open(\'{}\') after 3 retries'.format(path))

    def removedir(self, path, recursive=False, force=False):
        return super(BaseWrapper, self).removedir(path, recursive, force)

    def remove(self, path, lock_check=True):
        if lock_check:
            self._check_lock(path, op='remove')
        return super(BaseWrapper, self).remove(path)

    def move(self, path_old, path_new, overwrite=False, chunk_size=16384, lock_check=True):
        if lock_check:
            self._check_lock(path_old, op='move')
        return super(BaseWrapper, self).move(path_old, path_new, overwrite, chunk_size)

    def copy(self, src, dst, overwrite=False, chunk_size=None, lock_check=True):
        if lock_check:
            self._check_lock(src, op='copy')
        return super(BaseWrapper, self).copy(src, dst, overwrite, chunk_size)

    def ensuredir(self, filename):
        """ Ensure that the directory path for ``filename`` exists """
        dirname = os.path.dirname(filename)
        if dirname:
            try:
                self.makedir(dirname, recursive=True)
            except fs.errors.DestinationExistsError:
                pass

    def convert_string(self, s):
        """ Convert string according to FS unicode_paths metadata """
        if issubclass(self.__class__, fs.osfs.OSFS):
            return unidecode.unidecode(s).encode('utf8')
        if not self.getmeta('unicode_paths') and isinstance(s, unicode):
            return s.encode('utf-8')
        return s


class DAVFSWrapper(BaseWrapper, DAVFS):
    pass


class OSFSWrapper(BaseWrapper, OSFS):
    pass


class FTPFSWrapper(BaseWrapper, FTPFS):
    pass


if have_paramiko:
    from fs.sftpfs import SFTPFS

    class SFTPFSWrapper(BaseWrapper, SFTPFS):
        pass


if have_boto:
    from fs.s3fs import S3FS

    class S3FSWrapper(BaseWrapper, S3FS):
        pass


if have_dropbox:
    from xmldirector.dropbox.browser.dropboxfs import DropboxFS

    class DropboxFSWrapper(BaseWrapper, DropboxFS):

        supports_locks = False


def get_fs_wrapper(url, credentials=None, context=None):

    if not url:
        raise ValueError('No connector URL configured - either set a connector URL '
                         'in Plone Site-Setup -> XML Director settings or '
                         'configure the connector URL locally on the ' 
                         'current connector content object')

    if not url.endswith('/'):
        url += '/'
    f = furl(url)
    original_url = url
    if f.scheme == 'file':
        path = unicode(urllib.unquote(str(f.path)), 'utf8')
        wrapper = OSFSWrapper(path, encoding='utf-8')
    elif f.scheme.startswith(('http', 'https')):
        try:
            wrapper = DAVFSWrapper(original_url, credentials)
        except fs.errors.ResourceNotFoundError:
            LOG.info('Failed to get DAVFSWrapper for {}'.format(
                original_url), exc_info=True)
            raise NotFound(original_url)
        except Exception as e:
            LOG.error('Failed to get DAVFSWrapper for {}'.format(
                original_url), exc_info=True)
            raise e
    elif f.scheme == 's3':
        if have_boto:
            wrapper = S3FSWrapper(
                bucket=f.host,
                prefix=str(f.path),
                aws_access_key=credentials['username'],
                aws_secret_key=credentials['password'])
        else:
            raise ImportError(
                'boto module is not installed (required for S3 access)')
    elif f.scheme == 'sftp':

        f_path = urllib.unquote(str(f.path))
        if have_paramiko:
            wrapper = SFTPFSWrapper(connection=(f.host, f.port or 22),
                                    root_path=f_path,
                                    username=(credentials['username'] or None),
                                    password=(credentials['password'] or None))

            if wrapper.isfile('.') and wrapper.isdir('.'):
                parts = filter(None, f_path.split('/'))
                wrapper = SFTPFSWrapper(connection=(f.host, f.port or 22),
                                        root_path='/'.join(parts[:-1]),
                                        username=(
                                            credentials['username'] or None),
                                        password=(credentials['password'] or None))
                wrapper.__leaf__ = True
                wrapper.__leaf_filename__ = parts[-1]
        else:
            raise ImportError(
                'paramiko module is not installed (required for SFTP access)')

    elif f.scheme == 'ftp':
        wrapper = FTPFSWrapper(host=f.host,
                               port=f.port,
                               user=credentials['username'],
                               passwd=credentials['password'])

    elif f.scheme == 'dropbox':

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDropboxSettings)
        annotation = IAnnotations(context)

        token_key = annotation.get(dropbox_authentication.DROPBOX_TOKEN_KEY)
        token_secret = annotation.get(
            dropbox_authentication.DROPBOX_TOKEN_SECRET)
        if not token_key or not token_secret:
            context = zope.globalrequest.getRequest().PUBLISHED.context
            authorization_url = '{}/authorize-dropbox'.format(
                context.absolute_url())
            raise RequiresAuthorizationError(
                'Connector does not seem to be authorized against Dropbox',
                authorization_url)

        wrapper = DropboxFSWrapper(
            settings.dropbox_app_key,
            settings.dropbox_app_secret,
            'dropbox',
            annotation[dropbox_authentication.DROPBOX_TOKEN_KEY],
            annotation[dropbox_authentication.DROPBOX_TOKEN_SECRET],
            root_path=urllib.unquote(str(f.path))
        )

        if wrapper.isfile('.'):
            wrapper.__leaf__ = True
            wrapper.__leaf_filename__ = '.'

    else:
        raise ValueError('Unsupported URL schema {}'.format(original_url))

    wrapper.url = url
    return wrapper
