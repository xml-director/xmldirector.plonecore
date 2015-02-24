################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


from fs.contrib.davfs import DAVFS
from fs import iotools


class DAVFSWrapper(DAVFS):
    """ A wapper for DAVFS """

    @iotools.filelike_to_stream
    def open(self,path,mode="r", **kwargs):
        return super(DAVFSWrapper, self).open(path, mode, **kwargs)
