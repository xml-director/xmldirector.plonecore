################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


from fs.contrib.davfs import DAVFS
from fs import iotools

from xmldirector.plonecore.locking import FileIsLocked

class DAVFSWrapper(DAVFS):
    """ A wapper for DAVFS """

    def _lock_filename(self, path):
        return '{}.lock.xml'.format(path)

    @iotools.filelike_to_stream
    def open(self,path,mode="r", **kwargs):
        lock_filename = self._lock_filename(path)
        if mode.startswith('w') and self.exists(lock_filename):
            raise FileIsLocked('File is locked and can not be written ({})'.format(path))
        return super(DAVFSWrapper, self).open(path, mode, **kwargs)
    
    def remove(self, path):
        lock_filename = self._lock_filename(path)
        if self.exists(lock_filename):
            raise FileIsLocked('File is locked and can not be removed ({})'.format(path))
        return super(DAVFSWrapper, self).remove(path)

    def move(self, old, new):
        lock_filename = self._lock_filename(old)
        if self.exists(lock_filename):
            raise FileIsLocked('File is locked and can not be moved ({})'.format(old))
        return super(DAVFSWrapper, self).move(old, new)

