import os
import datetime
from fs.contrib.davfs import DAVFS
from fs.osfs import OSFS
import fs.utils
import uuid

source = OSFS('/tmp/bookalope')
target = DAVFS('http://localhost:6080/exist/webdav/db', credentials=dict(username='admin', password='onkopedia'))
target = DAVFS('http://localhost:8984/webdav', credentials=dict(username='admin', password='admin'))


print source.listdir()
print target.listdir()

def copy(source, source_dir, target, target_dir):

    original_target_dir = target_dir
    target_dir = 'copy-{}-{}'.format(str(uuid.uuid4()), datetime.datetime.utcnow().isoformat())

    if not source.exists(source_dir):
        raise ValueError('{} does not exist'.format(source_dir))

    dirs_seen = []
    for name in source.walkfiles(source_dir):
        print name
        dirname = os.path.dirname(name)
        if not dirname in dirs_seen:
            target_directory = os.path.join(target_dir, dirname)
            if not target.exists(target_directory):
                target.makedir(target_directory, recursive=True)

        target_filename = os.path.join(target_dir, name)
        with source.open(name, 'rb') as fp_in, \
             target.open(target_filename, 'wb') as fp_out:
                 fp_out.write(fp_in.read())

    if not target.exists(original_target_dir):
        target.makedir(original_target_dir, recursive=True)
    import pdb; pdb.set_trace() 
    target.rename(os.path.join(target_dir, source_dir), original_target_dir)

copy(source, 'zopyx-nimbudocs', target, 'dest')

