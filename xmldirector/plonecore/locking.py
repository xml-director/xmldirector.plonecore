################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


"""
Locking Manager
"""

import fs
import dateutil
import lxml.etree
from datetime import datetime
import uuid
import plone.api
from zope.component import getUtility
from xmldirector.plonecore.interfaces import IWebdavHandle


lock_xml_template = '''<lock version="1.0"
token="{token}"
created="{created}"
owner="{owner}"
valid="{valid}"
mode="{mode}"
/>'''


class UnlockError(Exception):
    pass

class LockError(Exception):
    pass


class LockManager(object):

    def __init__(self, context):
        self.context = context

    @property
    def webdav_handle(self):
        return getUtility(IWebdavHandle).webdav_handle()

    def lock_filename(self, path):
        return '{}.lock.xml'.format(path)

    def has_lock(self, path):
        handle = self.webdav_handle
        return handle.exists(self.lock_filename(path))

    def get_lock(self, path):
        
        handle = self.webdav_handle
        lock_filename = self.lock_filename(path)
        with handle.open(lock_filename, 'rb') as fp:
            lock_xml = fp.read()
        root = lxml.etree.fromstring(lock_xml)
        lock_info = dict()
        lock_info['mode'] = root.attrib['mode']
        lock_info['owner'] = root.attrib['owner']
        lock_info['token'] = root.attrib['token']
        lock_info['valid'] = root.attrib['valid']
        lock_info['created'] = dateutil.parser.parse(root.attrib['created'])
        return lock_info

    def lock(self, path, mode='shared', lifetime=None):

        if not mode in ('shared', 'exclusive'):
            raise LockError(u'mode must be either "shared" or "exclusive"')

        handle = self.webdav_handle
        if not handle.exists(path):
            raise LockError('Lock target does not exist ({})'.format(path))

        lock_filename = self.lock_filename(path)
        if handle.exists(lock_filename):
            raise LockError('Already locked ({})'.format(path))

        valid = ''
        lock_info = dict(
                token=str(uuid.uuid4()),
                owner= plone.api.user.get_current().getUserName(),
                created=datetime.utcnow().isoformat(),
                mode=mode,
                valid=valid)
        lock_xml = lock_xml_template.format(**lock_info)
        with handle.open(lock_filename, 'wb') as fp:
            fp.write(lock_xml)
        return lock_info

    def unlock(self, path, token):

        handle = self.webdav_handle
        lock_filename = self.lock_filename(path)
        try:
            handle.remove(lock_filename)
        except fs.errors.ResourceNotFoundError:
            raise UnlockError('Lock not found ({})'.format(path))

