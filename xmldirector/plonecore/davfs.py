# -*- coding: utf-8 -*-


################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


from collections import namedtuple
from fs.contrib.davfs import DAVFS
from fs import iotools

import plone.api
from xmldirector.plonecore.locking import LockManager
from xmldirector.plonecore.locking import FileIsLocked
from xmldirector.plonecore.locking import LockError


_marker = object

lockstate = namedtuple('lockstate', 'op, mode, lock_owner')

# LOCK MODES

EXCL = 'exclusive'
SHRD = 'shared'


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


class DAVFSWrapper(DAVFS):

    """ A wapper for DAVFS """

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
        return super(DAVFSWrapper, self).open(path, mode, **kwargs)

    def remove(self, path, lock_check=True):
        if lock_check:
            self._check_lock(path, op='remove')
        return super(DAVFSWrapper, self).remove(path)

    def move(self, path_old, path_new, lock_check=True):
        if lock_check:
            self._check_lock(path_old, op='move')
        return super(DAVFSWrapper, self).move(path_old, path_new)

    def copy(self, src, dst, overwrite=False, chunk_size=None, lock_check=True):
        if lock_check:
            self._check_lock(src, op='copy')
        return super(DAVFSWrapper, self).copy(src, dst, overwrite, chunk_size)
