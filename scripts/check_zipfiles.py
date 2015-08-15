import fs.zipfs
import sys
import zipfile


fname = sys.argv[-1]

print 'zipfile.ZipFile'
zf = zipfile.ZipFile(fname, 'r')
for name in zf.namelist():
    print name, type(name), repr(name)

print 'fs.zipfs.ZipFS'
zf = fs.zipfs.ZipFS(fname, 'r')
for name in zf.listdir():
    print type(name), repr(name)
