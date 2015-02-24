################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


from fs.contrib.davfs import DAVFS
from fs import iotools

def check_locks(method):
    """ Decorator to register a method as a transformation"""
    def _check_locks(self, *args, **kw):
        return method(self, *args, **kw)
    return _check_locks


class DAVFSWrapper(DAVFS):
    """ A wapper for DAVFS """

    @iotools.filelike_to_stream
    @check_locks
    def open(self,path,mode="r", **kwargs):
        return super(DAVFSWrapper, self).open(path, mode, **kwargs)
