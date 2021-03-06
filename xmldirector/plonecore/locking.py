# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


"""
Locking Manager.

The locking manager provides a simple lock mechanism for single
XML files within the XML database by adding a .lock.xml file containing
additional metadata related to the lock and/or application.
"""

import fs
import uuid
import dateutil
import defusedxml.lxml
from datetime import datetime

import plone.api
from zope.component import getUtility
from xmldirector.plonecore.interfaces import IConnectorHandle


lock_xml_template = u'''<lock version="1.0"
token="{token}"
created="{created}"
owner="{owner}"
valid="{valid}"
mode="{mode}"
>
{custom}
</lock>'''


class UnlockError(Exception):

    """ Exception for unlock operations """


class LockError(Exception):

    """ Exception for lock operations """


class AlreadyLockedError(Exception):

    """ File already locked """


class FileIsLocked(Exception):

    """ Exception for disallowed operations on locked files """


class LockManager(object):

    def __init__(self, context=None):
        self.context = context

    @property
    def get_handle(self):
        """ Return webdav handle as property """
        from xmldirector.plonecore.fswrapper import get_fs_wrapper
        if self.context:
            context = self.context
        else:
            try:
                context = plone.api.portal.get().REQUEST.PUBLISHED.context
            except AttributeError:
                context = None
        if context:
            context_connector_url = getattr(context, 'connector_url', None)
            if context_connector_url:
                username = context.connector_username
                password = context.connector_password
                if username and password:
                    return get_fs_wrapper(
                        context_connector_url,
                        credentials=dict(username=username, password=password),
                        context=self.context)
                else:
                    return get_fs_wrapper(context_connector_url, context=self.context)
        return getUtility(IConnectorHandle).get_handle()

    def lock_filename(self, path):
        """ Canoncial lock filename for a given path """
        if not isinstance(path, unicode):
            path = unicode(path, 'utf8')
        return u'{}.lock.xml'.format(path).encode('utf-8')

    def has_lock(self, path):
        """ Return True if the given file is locked, False otherwise """
        handle = self.get_handle
        return handle.exists(self.lock_filename(path))

    def get_lock(self, path):
        """ Retrieve lock information """
        if not isinstance(path, unicode):
            path = unicode(path, 'utf8')

        handle = self.get_handle
        lock_filename = self.lock_filename(path)
        try:
            with handle.open(lock_filename, 'rb', lock_check=False) as fp:
                lock_xml = fp.read()
        except fs.errors.ResourceNotFoundError:
            raise LockError(u'No lock file found for {}'.format(path))

        root = defusedxml.lxml.fromstring(lock_xml)
        lock_info = dict()
        lock_info['mode'] = root.attrib['mode']
        lock_info['owner'] = root.attrib['owner']
        lock_info['token'] = root.attrib['token']
        lock_info['valid'] = root.attrib['valid']
        lock_info['created'] = dateutil.parser.parse(root.attrib['created'])
        lock_info['custom'] = dict()
        for node in root.xpath('//value'):
            lock_info['custom'][node.attrib['name']] = node.text
        return lock_info

    def lock(self, path, mode='shared', lifetime=None, custom=None):
        """ Lock the given path in mode shared|exclusive.
            mode=shared - file can be read but not modified.
            mode=exclusive - file can not read, only written.
        """

        custom = custom or {}

        if mode not in ('shared', 'exclusive'):
            raise LockError(u'mode must be either "shared" or "exclusive"')

        handle = self.get_handle
        if not handle.exists(path):
            raise LockError('Lock target does not exist ({})'.format(path))

        if not handle.isfile(path):
            raise LockError('Only files can be locked({})'.format(path))

        lock_filename = self.lock_filename(path)
        if handle.exists(lock_filename):
            raise AlreadyLockedError('Already locked ({})'.format(path))

        valid = ''
        custom = u''.join(
            [u'<value name="{}">{}</value>'.format(k, v) for k, v in custom.items()])
        lock_info = dict(
            token=str(uuid.uuid4()),
            owner=plone.api.user.get_current().getUserName(),
            created=datetime.utcnow().isoformat(),
            mode=mode,
            valid=valid,
            custom=custom)
        lock_xml = lock_xml_template.format(**lock_info)
        with handle.open(lock_filename, 'wb', lock_check=False) as fp:
            fp.write(lock_xml)
        return lock_info

    def unlock(self, path, token, force=False):
        """ Unlock a file lock using a given lock token.
            The stored lock token and the given token must match
            in order to release the lock successfully.
        """

        handle = self.get_handle

        lock_info = self.get_lock(path)
        lock_token = lock_info['token']
        if not force and token != lock_token:
            raise UnlockError('Lock tokens differ')

        try:
            handle.remove(self.lock_filename(path))
        except fs.errors.ResourceNotFoundError:
            raise UnlockError('Lock not found ({})'.format(path))
