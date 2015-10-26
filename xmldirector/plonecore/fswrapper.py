# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import urllib
from furl import furl

from fs.osfs import OSFS
from fs.ftpfs import FTPFS
from fs import iotools
from fs.contrib.davfs import DAVFS
from collections import namedtuple

import plone.api
from xmldirector.plonecore.locking import LockManager
from xmldirector.plonecore.locking import FileIsLocked
from xmldirector.plonecore.locking import LockError


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


class BaseWrapper(object):
    """ A wapper for DAVFS """

    def isDirectory(self):
        """ Represents a directory """
        __leaf__ = getattr(self, '__leaf__', _marker)
        if __leaf__ != _marker:
            return not getattr(self, '__leaf__', False)
        if isinstance(self, SFTPFSWrapper):
            return not self.isfile('.')
        return self.isdir('.')

    def isFile(self):
        """ Represents a file """
        __leaf__ = getattr(self, '__leaf__', _marker)
        if __leaf__ != _marker:
            return getattr(self, '__leaf__', False)
        if isinstance(self, SFTPFSWrapper):
            return self.isfile('.')
        return self.isfile('.')

    @property
    def leaf_filename(self):
        __leaf__ = getattr(self, '__leaf__', _marker)
        if __leaf__ != _marker:
            # hack for OSFS, fix this
            return urllib.unquote(self.__leaf_filename__)
        if isinstance(self, SFTPFSWrapper):
            return '.'
        if self.isFile():
            return '.'
        return '.'

    def _check_lock(self, path, op):

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
        if allowed is _marker:
            raise ValueError('No entry found for ({})'.format(msg))
        if not allowed:
            raise FileIsLocked('File is locked ({})'.format(msg))

    @iotools.filelike_to_stream
    def open(self, path, mode="r", lock_check=True, **kwargs):
        if lock_check:
            self._check_lock(path, op='open_{}'.format(mode[0]))
        return super(BaseWrapper, self).open(path, mode, **kwargs)

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


def get_fs_wrapper(url, credentials=None):

    if not url.endswith('/'):
        url += '/'
    f = furl(url)
    original_url = url
    if f.scheme == 'file':
        # hack for OSFP, fix this
        path = urllib.unquote(url[7:])
        wrapper = OSFSWrapper(path, encoding='utf-8')
    elif f.scheme == 'http':
        wrapper = DAVFSWrapper(original_url, credentials)
    elif f.scheme == 'https':
        wrapper = DAVFSWrapper(original_url, credentials)
    elif f.scheme == 's3':
        if have_boto:
            wrapper = S3FSWrapper(
                bucket=f.host,
                prefix=str(f.path),
                aws_access_key=credentials['username'],
                aws_secret_key=credentials['password'])
        else:
            raise ImportError('boto module is not installed (required for S3 access)')
    elif f.scheme == 'sftp':

        if have_paramiko:
            wrapper = SFTPFSWrapper(connection=f.host,
                                    root_path=str(f.path),
                                    username=f.username,
                                    password=f.password)

            if wrapper.isfile('.') and wrapper.isdir('.'):
                parts = filter(None, str(f.path).split('/'))
                wrapper = SFTPFSWrapper(connection=f.host,
                                        root_path='/'.join(parts[:-1]),
                                        username=f.username,
                                        password=f.password)
                wrapper.__leaf__ = True
                wrapper.__leaf_filename__ = parts[-1]
        else:
            raise ImportError('paramiko module is not installed (required for SFTP access)')

    elif f.scheme == 'ftp':
        wrapper = FTPFSWrapper(host=f.host,
                               user=credentials['username'],
                               passwd=credentials['password'])
    else:
        raise ValueError('Unsupported URL schema {}'.format(original_url))

    wrapper.url = url
    return wrapper

