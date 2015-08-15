import fs.zipfs
import sys
import zipfile


fname = sys.argv[-1]

print 'zipfile.ZipFile'
zf = zipfile.ZipFile(fname, 'r')
for name in zf.namelist():
    print name, type(name), repr(name)

print 'fs.zipfs.ZipFS'
zf = fs.zipfs.ZipFS(fname, 'r', encoding='utf8')
for dirname, filenames in zf.walk():
    for name in filenames:
        print name.encode('utf8'), type(name), repr(name)
