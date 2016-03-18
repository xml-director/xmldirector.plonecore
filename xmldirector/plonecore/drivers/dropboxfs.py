"""
fs.contrib.dropboxfs
========

A FS object that integrates with Dropbox.

"""

import time
import shutil
import optparse
import datetime
import tempfile
import calendar
import logging
from UserDict import UserDict

from fs.base import *
from fs.path import *
from fs.errors import *
from fs.filelike import StringIO

from dropbox import rest
from dropbox import client
from dropbox import session


LOGGER = logging.getLogger(__name__)

# Items in cache are considered expired after 5 minutes.
CACHE_TTL = 300
# The format Dropbox uses for times.
TIME_FORMAT = '%a, %d %b %Y %H:%M:%S +0000'
# Max size for spooling to memory before using disk (5M).
MAX_BUFFER = 1024 ** 2 * 5


class ContextManagerStream(object):

    def __init__(self, temp, name):
        self.temp = temp
        self.name = name

    def __iter__(self):
        while True:
            data = self.read(16384)
            if not data:
                break
            yield data

    def __getattr__(self, name):
        return getattr(self.temp, name)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# TODO: these classes can probably be replaced with
# tempfile.SpooledTemporaryFile, however I am unsure at this moment if doing
# so would be bad since it is only available in Python 2.6+.

class SpooledWriter(ContextManagerStream):
    """Spools bytes to a StringIO buffer until it reaches max_buffer. At that
    point it switches to a temporary file."""

    def __init__(self, client, name, max_buffer=MAX_BUFFER):
        self.client = client
        self.max_buffer = max_buffer
        self.bytes = 0
        super(SpooledWriter, self).__init__(StringIO(), name)

    def __len__(self):
        return self.bytes

    def write(self, data):
        if self.temp.tell() + len(data) >= self.max_buffer:
            # We reached the max_buffer size that we want to keep in memory.
            # Switch to an on-disk temp file. Copy what has been written so
            # far to it.
            temp = tempfile.TemporaryFile()
            self.temp.seek(0)
            shutil.copyfileobj(self.temp, temp)
            self.temp = temp
        self.temp.write(data)
        self.bytes += len(data)

    def close(self):
        # Need to flush temporary file (but not StringIO).
        if hasattr(self.temp, 'flush'):
            self.temp.flush()
        self.temp.seek(0)
        self.client.put_file(self.name, self, overwrite=True)
        self.temp.close()


class SpooledReader(ContextManagerStream):
    """
    Reads the entire file from the remote server into a buffer or temporary
    file. It can then satisfy read(), seek() and other calls using the local
    file.
    """

    def __init__(self, client, name, max_buffer=MAX_BUFFER):
        self.client = client
        r = self.client.get_file(name)
        self.bytes = int(r.getheader('Content-Length'))
        if r > max_buffer:
            temp = tempfile.TemporaryFile()
        else:
            temp = StringIO()
        shutil.copyfileobj(r, temp)
        temp.seek(0)
        super(SpooledReader, self).__init__(temp, name)

    def __len__(self):
        return self.bytes


class ChunkedReader(ContextManagerStream):
    """ A file-like that provides access to a file with dropbox API"""
    """Reads the file from the remote server as requested.
    It can then satisfy read()."""

    def __init__(self, client, name):
        self.client = client
        try:
            self.r = self.client.get_file(name)
        except rest.ErrorResponse, e:
            LOGGER.error(e, exc_info=True, extra={'stack': True, })
            raise RemoteConnectionError(opname='get_file', path=name,
                                        details=e)
        self.bytes = int(self.r.getheader('Content-Length'))
        self.name = name
        self.closed = False
        self.pos = 0
        self.seek_pos = 0

    def __len__(self):
        return self.bytes

    def __iter__(self):
        return self

    def seek(self, offset, whence=0):
        """
        Change the stream position to the given byte offset in the file-like
        object.
        """
        if (whence == 0):
            self.seek_pos = offset
        elif (whence == 1):
            self.seek_pos += offset
        elif (whence == 2):
            self.seek_pos = self.size + offset

    def tell(self):
        """ Return the current stream position. """
        return self.seek_pos

    def next(self):
        """
        Read the data until all data is read.
        data is empty string when there is no more data to read.
        """
        data = self.read()
        if data is None:
            raise StopIteration()
        return data

    def read(self, amt=None):
        """ Read a piece of the file from dropbox. """
        if not self.r.isclosed():
            # Do some fake seeking
            if self.seek_pos < self.pos:
                self.r.close()
                self.r = self.client.get_file(self.name)
                self.r.read(self.seek_pos)
            elif self.seek_pos > self.pos:
                # Read ahead enough to reconcile pos and seek_pos
                self.r.read(self.pos - self.seek_pos)
            self.pos = self.seek_pos

            # Update position pointers
            if amt:
                self.pos += amt
                self.seek_pos += amt
            else:
                self.pos = self.bytes
                self.seek_pos = self.bytes
            return self.r.read(amt)
        else:
            self.close()

    def readline(self, size=-1):
        """ Not implemented. Read and return one line from the stream. """
        raise NotImplementedError()

    def readlines(self, hint=-1):
        """
        Not implemented. Read and return a list of lines from the stream.
        """
        raise NotImplementedError()

    def writable(self):
        """ The stream does not support writing. """
        return False

    def writelines(self, lines):
        """ Not implemented. Write a list of lines to the stream. """
        raise NotImplementedError()

    def close(self):
        """
        Flush and close this stream. This method has no effect if the file
        is already closed. As a convenience, it is allowed to call this method
        more than once; only the first call, however, will have an effect.
        """
        # It's a memory leak if self.r not closed.
        if not self.r.isclosed():
            self.r.close()
        if not self.closed:
            self.closed = True


class CacheItem(object):
    """Represents a path in the cache. There are two components to a path.
    It's individual metadata, and the children contained within it."""

    def __init__(self, metadata=None, children=None, timestamp=None):
        self.metadata = metadata
        self.children = children
        if timestamp is None:
            timestamp = time.time()
        self.timestamp = timestamp

    def add_child(self, name):
        if self.children is None:
            self.children = [name]
        else:
            self.children.append(name)

    def del_child(self, name):
        if self.children is None:
            return
        try:
            i = self.children.index(name)
        except ValueError:
            return
        self.children.pop(i)

    def _get_expired(self):
        if self.timestamp <= time.time() - CACHE_TTL:
            return True
    expired = property(_get_expired)

    def renew(self):
        self.timestamp = time.time()


class DropboxCache(UserDict):

    def set(self, path, metadata):
        self[path] = CacheItem(metadata)
        dname, bname = pathsplit(path)
        item = self.get(dname)
        if item:
            item.add_child(bname)

    def pop(self, path, default=None):
        value = UserDict.pop(self, path, default)
        dname, bname = pathsplit(path)
        item = self.get(dname)
        if item:
            item.del_child(bname)
        return value


class DropboxClient(client.DropboxClient):
    """A wrapper around the official DropboxClient. This wrapper performs
    caching as well as converting errors to fs exceptions."""

    def __init__(self, *args, **kwargs):
        super(DropboxClient, self).__init__(*args, **kwargs)
        self.cache = DropboxCache()

    # Below we split the DropboxClient metadata() method into two methods
    # metadata() and children(). This allows for more fine-grained fetches
    # and caching.

    def metadata(self, path, cache_read=True):
        "Gets metadata for a given path."
        item = self.cache.get(path) if cache_read else None
        if not item or item.metadata is None or item.expired:
            try:
                metadata = super(DropboxClient, self).metadata(
                    path, include_deleted=False, list=False)
            except rest.ErrorResponse, e:
                if e.status == 404:
                    raise ResourceNotFoundError(path)
                LOGGER.error(e, exc_info=True, extra={'stack': True, })
                raise RemoteConnectionError(opname='metadata', path=path,
                                            details=e)
            if metadata.get('is_deleted', False):
                raise ResourceNotFoundError(path)
            item = self.cache[path] = CacheItem(metadata)
        # Copy the info so the caller cannot affect our cache.
        return dict(item.metadata.items())

    def children(self, path):
        "Gets children of a given path."
        update, hash = False, None
        item = self.cache.get(path)
        if item:
            if item.expired:
                update = True
                if item.metadata and item.children:
                    hash = item.metadata['hash']
            else:
                if not item.metadata.get('is_dir'):
                    raise ResourceInvalidError(path)
            if not item.children:
                update = True
        else:
            update = True
        if update:
            try:
                metadata = super(DropboxClient, self).metadata(
                    path, hash=hash, include_deleted=False, list=True)
                children = []
                contents = metadata.pop('contents')
                for child in contents:
                    if child.get('is_deleted', False):
                        continue
                    children.append(basename(child['path']))
                    self.cache[child['path']] = CacheItem(child)
                item = self.cache[path] = CacheItem(metadata, children)
            except rest.ErrorResponse, e:
                if not item or e.status != 304:
                    LOGGER.error(e, exc_info=True, extra={'stack': True, })
                    raise RemoteConnectionError(opname='metadata', path=path,
                                                details=e)
                # We have an item from cache (perhaps expired), but it's
                # hash is still valid (as far as Dropbox is concerned),
                # so just renew it and keep using it.
                item.renew()
        return item.children

    def file_create_folder(self, path):
        "Add newly created directory to cache."
        try:
            metadata = super(DropboxClient, self).file_create_folder(path)
        except rest.ErrorResponse, e:
            if e.status == 404:
                raise ParentDirectoryMissingError(path)
            if e.status == 403:
                raise DestinationExistsError(path)
            LOGGER.error(e, exc_info=True, extra={'stack': True, })
            raise RemoteConnectionError(opname='file_create_folder', path=path,
                                        details=e)
        self.cache.set(path, metadata)

    def file_copy(self, src, dst):
        try:
            metadata = super(DropboxClient, self).file_copy(src, dst)
        except rest.ErrorResponse, e:
            if e.status == 404:
                raise ResourceNotFoundError(src)
            if e.status == 403:
                raise DestinationExistsError(dst)
            LOGGER.error(e, exc_info=True, extra={'stack': True, })
            raise RemoteConnectionError(opname='file_copy', path=path,
                                        details=e)
        self.cache.set(dst, metadata)

    def file_move(self, src, dst):
        try:
            metadata = super(DropboxClient, self).file_move(src, dst)
        except rest.ErrorResponse, e:
            if e.status == 404:
                raise ResourceNotFoundError(src)
            if e.status == 403:
                raise DestinationExistsError(dst)
            LOGGER.error(e, exc_info=True, extra={'stack': True, })
            raise RemoteConnectionError(opname='file_move', path=path,
                                        details=e)
        self.cache.pop(src, None)
        self.cache.set(dst, metadata)

    def file_delete(self, path):
        try:
            super(DropboxClient, self).file_delete(path)
        except rest.ErrorResponse, e:
            if e.status == 404:
                raise ResourceNotFoundError(path)
            if e.status == 400 and 'must not be empty' in str(e):
                raise DirectoryNotEmptyError(path)
            raise
        self.cache.pop(path, None)

    def put_file(self, path, f, overwrite=False):
        try:
            super(DropboxClient, self).put_file(path, f, overwrite=overwrite)
        except rest.ErrorResponse, e:
            LOGGER.error(e, exc_info=True, extra={'stack': True, })
            raise RemoteConnectionError(opname='put_file', path=path,
                                        details=e)
        self.cache.pop(dirname(path), None)


def create_client(app_key, app_secret, access_type, token_key, token_secret):
    """Uses token from create_token() to gain access to the API."""
    s = session.DropboxSession(app_key, app_secret, access_type)
    s.set_token(token_key, token_secret)
    return DropboxClient(s)


def metadata_to_info(metadata, localtime=False):
    isdir = metadata.pop('is_dir', False)
    info = {
        'size': metadata.pop('bytes', 0),
        'isdir': isdir,
        'isfile': not isdir,
    }
    try:
        if 'client_mtime' in metadata:
            mtime = metadata.get('client_mtime')
        else:
            mtime = metadata.get('modified')
        if mtime:
            # Parse date/time from Dropbox as struct_time.
            mtime = time.strptime(mtime, TIME_FORMAT)
            if localtime:
                # Convert time to local timezone in seconds.
                mtime = calendar.timegm(mtime)
            else:
                mtime = time.mktime(mtime)
            # Convert to datetime object, store in modified_time
            info['modified_time'] = datetime.datetime.fromtimestamp(mtime)
    except KeyError:
        pass
    return info


class DropboxFS(FS):
    """A FileSystem that stores data in Dropbox."""

    _meta = {'thread_safe': True,
             'virtual': False,
             'read_only': False,
             'unicode_paths': True,
             'case_insensitive_paths': True,
             'network': True,
             'atomic.setcontents': False,
             'atomic.makedir': True,
             'atomic.rename': True,
             'mime_type': 'virtual/dropbox', }

    def __init__(self, app_key, app_secret, access_type, token_key,
                 token_secret, localtime=False, thread_synchronize=True):
        """Create an fs that interacts with Dropbox.

        :param app_key: Your app key assigned by Dropbox.
        :param app_secret: Your app secret assigned by Dropbox.
        :param access_type: Type of access requested, 'dropbox' or 'app_folder'.
        :param token_key: The oAuth key you received after authorization.
        :param token_secret: The oAuth secret you received after authorization.
        :param thread_synchronize: set to True (default) to enable thread-safety
        """
        super(DropboxFS, self).__init__(thread_synchronize=thread_synchronize)
        self.client = create_client(app_key, app_secret, access_type,
                                    token_key, token_secret)
        self.localtime = localtime

    def __str__(self):
        return "<DropboxFS: >"

    def __unicode__(self):
        return u"<DropboxFS: >"

    def getmeta(self, meta_name, default=NoDefaultMeta):
        if meta_name == 'read_only':
            return self.read_only
        return super(DropboxFS, self).getmeta(meta_name, default)

    @synchronize
    def open(self, path, mode="rb", **kwargs):
        if 'r' in mode:
            return ChunkedReader(self.client, path)
        else:
            return SpooledWriter(self.client, path)

    @synchronize
    def getcontents(self, path, mode="rb"):
        path = abspath(normpath(path))
        return self.open(self, path, mode).read()

    def setcontents(self, path, data, *args, **kwargs):
        path = abspath(normpath(path))
        self.client.put_file(path, data, overwrite=True)

    def desc(self, path):
        return "%s in Dropbox" % path

    def getsyspath(self, path, allow_none=False):
        "Returns a path as the Dropbox API specifies."
        if allow_none:
            return None
        return client.format_path(abspath(normpath(path)))

    def isdir(self, path):
        try:
            info = self.getinfo(path)
            return info.get('isdir', False)
        except ResourceNotFoundError:
            return False

    def isfile(self, path):
        try:
            info = self.getinfo(path)
            return not info.get('isdir', False)
        except ResourceNotFoundError:
            return False

    def exists(self, path):
        try:
            self.getinfo(path)
            return True
        except ResourceNotFoundError:
            return False

    def listdir(self, path="/", wildcard=None, full=False, absolute=False,
                dirs_only=False, files_only=False):
        path = abspath(normpath(path))
        children = self.client.children(path)
        return self._listdir_helper(path, children, wildcard, full, absolute,
                                    dirs_only, files_only)

    @synchronize
    def getinfo(self, path, cache_read=True):
        path = abspath(normpath(path))
        metadata = self.client.metadata(path, cache_read=cache_read)
        return metadata_to_info(metadata, localtime=self.localtime)

    def copy(self, src, dst, *args, **kwargs):
        src = abspath(normpath(src))
        dst = abspath(normpath(dst))
        self.client.file_copy(src, dst)

    def copydir(self, src, dst, *args, **kwargs):
        src = abspath(normpath(src))
        dst = abspath(normpath(dst))
        self.client.file_copy(src, dst)

    def move(self, src, dst, *args, **kwargs):
        src = abspath(normpath(src))
        dst = abspath(normpath(dst))
        self.client.file_move(src, dst)

    def movedir(self, src, dst, *args, **kwargs):
        src = abspath(normpath(src))
        dst = abspath(normpath(dst))
        self.client.file_move(src, dst)

    def rename(self, src, dst, *args, **kwargs):
        src = abspath(normpath(src))
        dst = abspath(normpath(dst))
        self.client.file_move(src, dst)

    def makedir(self, path, recursive=False, allow_recreate=False):
        path = abspath(normpath(path))
        self.client.file_create_folder(path)

    # This does not work, httplib refuses to send a Content-Length: 0 header
    # even though the header is required. We can't make a 0-length file.
    # def createfile(self, path, wipe=False):
    #    self.client.put_file(path, '', overwrite=False)

    def remove(self, path):
        path = abspath(normpath(path))
        self.client.file_delete(path)

    def removedir(self, path, *args, **kwargs):
        path = abspath(normpath(path))
        self.client.file_delete(path)


def main():

    from ConfigParser import ConfigParser

    cp = ConfigParser()
    cp.read(['dropbox.ini'])

    section = 'test'
    app_key = cp.get(section, 'app_key')
    app_secret = cp.get(section, 'app_secret')
    access_token = cp.get(section, 'access_token')
    access_token_secret = cp.get(section, 'access_token_secret')

    parser = optparse.OptionParser(prog="dropboxfs",
                                   description="CLI harness for DropboxFS.")
    parser.add_option(
        "-k",
        "--app-key",
        default=app_key,
        help="Your Dropbox app key.")
    parser.add_option(
        "-s",
        "--app-secret",
        default=app_secret,
        help="Your Dropbox app secret.")
    parser.add_option(
        "-t",
        "--type",
        default='dropbox',
        choices=('dropbox', 'app_folder'),
        help="Your Dropbox app access type.")
    parser.add_option(
        "-a",
        "--token-key",
        default=access_token,
        help="Your access token key (if you previously obtained one.")
    parser.add_option(
        "-b",
        "--token-secret",
        default=access_token_secret,
        help="Your access token secret (if you previously obtained one.")

    (options, args) = parser.parse_args()

    # Can't operate without these parameters.
    if not options.app_key or not options.app_secret:
        parser.error(
            'You must obtain an app key and secret from Dropbox at the following URL.\n\nhttps://www.dropbox.com/developers/apps')

    # Instantiate a client one way or another.
    if not options.token_key and not options.token_secret:
        s = session.DropboxSession(options.app_key, options.app_secret,
                                   options.type)
        # Get a temporary token, so we can make oAuth calls.
        t = s.obtain_request_token()
        print "Please visit the following URL and authorize this application.\n"
        print s.build_authorize_url(t)
        print "\nWhen you are done, please press <enter>."
        raw_input()
        # Trade up to permanent access token.
        a = s.obtain_access_token(t)
        token_key, token_secret = a.key, a.secret
        print 'Your access token will be printed below, store it for later use.'
        print 'For future accesses, you can pass the --token-key and --token-secret'
        print ' arguments.\n'
        print 'Access token:', a.key
        print 'Access token secret:', a.secret
        print "\nWhen you are done, please press <enter>."
        raw_input()
    elif not options.token_key or not options.token_secret:
        parser.error('You must provide both the access token and the '
                     'access token secret.')
    else:
        token_key, token_secret = options.token_key, options.token_secret

    fs = DropboxFS(options.app_key, options.app_secret, options.type,
                   token_key, token_secret)

    print fs.getinfo('/')
    for x in fs.walk('ajung'):
        print x
#    print fs.getinfo('/Public')
#    if fs.exists('/Bar'):
#        fs.removedir('/Bar')
#    print fs.listdir('/')
#    fs.makedir('/Bar')
#    print fs.listdir('/')
#    print fs.listdir('/Foo')
#
#    filelike = fs.open('/big-file.pdf')
#    print filelike.read(100)
#    filelike.seek(100)
#    chunk2 = filelike.read(100)
#    print chunk2
#    filelike.seek(200)
#    print filelike.read(100)
#    filelike.seek(100)
#    chunk2a = filelike.read(100)
#    print chunk2a
#    assert chunk2 == chunk2a

if __name__ == '__main__':
    main()
