################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


from fs.contrib.davfs import DAVFS
from fs import iotools

import plone.api
from xmldirector.plonecore.locking import LockManager
from xmldirector.plonecore.locking import FileIsLocked
from xmldirector.plonecore.locking import LockError


class DAVFSWrapper(DAVFS):
    """ A wapper for DAVFS """

    def _lock_filename(self, path):
        return '{}.lock.xml'.format(path)

    def _resource_locked(self, path):
        lm = LockManager(None)
        try:
            log_info = lm.get_lock(path)
        except LockError:
            return False
        if log_info:
            owner = log_info['owner']
            if owner != plone.api.user.get_current().getUserName():
                return True
        return False

    @iotools.filelike_to_stream
    def open(self, path, mode="r", lock_check=True, **kwargs):
        if lock_check and mode.startswith('w'):
            if self._resource_locked(path):
                raise FileIsLocked('File is locked and can not be written ({})'.format(path))
        return super(DAVFSWrapper, self).open(path, mode, **kwargs)
    
    def remove(self, path, lock_check=True):
        if lock_check:
            if self._resource_locked(path):
                raise FileIsLocked('File is locked and can not be removed ({})'.format(path))
        return super(DAVFSWrapper, self).remove(path)

    def move(self, old, new, lock_check=True):
        if lock_check:
            if self._resource_locked(old):
                raise FileIsLocked('File is locked and can not be moved ({})'.format(old))
        return super(DAVFSWrapper, self).move(old, new)

