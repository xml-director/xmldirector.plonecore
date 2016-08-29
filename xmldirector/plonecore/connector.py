# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import fs
import fs.errors
import urllib

import zExceptions
from zope import schema
from zope.interface import implements
from zope.component import getUtility
from plone.dexterity.content import Item
from plone.supermodel import model
from plone.registry.interfaces import IRegistry

from xmldirector.plonecore.i18n import MessageFactory as _
from xmldirector.plonecore.interfaces import IConnectorSettings
from xmldirector.plonecore.interfaces import IConnectorHandle
from xmldirector.plonecore.fswrapper import get_fs_wrapper
from xmldirector.plonecore.fswrapper import RequiresAuthorizationError
from xmldirector.plonecore.logger import LOG


class IConnector(model.Schema):

    connector_url = schema.TextLine(
        title=_(u'(optional) connection URL of storage'),
        description=_(u'WebDAV: http://host:port/path/to/webdav, '
                      'Local filesystem: file://path/to/directory, '
                      'AWS S3: s3://bucketname, ',
                      'SFTP sftp://host/path, '
                      'FTP: ftp://host/path'),
        required=False
    )

    connector_username = schema.TextLine(
        title=_(u'(optional) username overriding the system settings'),
        required=False
    )

    connector_password = schema.Password(
        title=_(u'(optional) password overriding the system settings'),
        required=False
    )

    connector_subpath = schema.TextLine(
        title=_(u'Subdirectory relative to the global connection URL'),
        description=_(
            u'Use this value for configuring a more specific subpath'),
        required=False
    )

    api_enabled = schema.Bool(
        title=_(u'Public web API enabled'),
        default=False,
        required=False
    )

    default_view_anonymous = schema.TextLine(
        title=_(u'Default view (anonymous)'),
        description=_(
            u'Name of a default view for site visitors without edit permission'),
        required=False,
        default=None,
    )

    default_view_authenticated = schema.TextLine(
        title=_(u'Default view (authenticated)'),
        description=_(u'Name of a default view for anonymous site visitors'),
        required=False,
        default=u'@@view',
    )


class Connector(Item):

    implements(IConnector)

    connector_url = None
    connector_username = None
    connector_password = None
    connector_subpath = None

    def get_handle(self, subpath=None, create_if_not_existing=False):
        """ Return WebDAV handle to root of configured connector object
            including configured connector_subpath.
        """

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IConnectorSettings)

        if isinstance(subpath, unicode):
            subpath = subpath.encode('utf8')

        adapted = IConnector(self)

        url = adapted.connector_url or settings.connector_url

        if adapted.connector_subpath:
            url += '/{}'.format(adapted.connector_subpath)

        if subpath:
            url += '/{}'.format(urllib.quote(subpath))

        # system-wide credentials
        username = settings.connector_username
        password = settings.connector_password or ''

        # local credentials override the system credentials
        if adapted.connector_url:
            username = adapted.connector_username or ''
            password = adapted.connector_password or ''

        if create_if_not_existing:
            util = getUtility(IConnectorHandle)
            handle = util.get_handle()
            if not handle.exists(adapted.connector_subpath):
                handle.makedir(adapted.connector_subpath, recursive=True)
            url = '{}/{}'.format(handle.url.strip('/'),
                                 adapted.connector_subpath)

        if not url:
            raise ValueError('No connector URL configured - either set a connector URL '
                             'in Plone Site-Setup -> XML Director settings or '
                             'configure the connector URL locally on the '
                             'current connector content object')

        try:
            return get_fs_wrapper(url, credentials=dict(username=username, password=password), context=self)
        except fs.errors.ResourceNotFoundError:
            LOG.warn(u'Error accessing {}::{}::{}'.format(
                self.absolute_url(), url, self.REQUEST.get('HTTP_USER_AGENT')), exc_info=True)
            raise zExceptions.NotFound(url)
        except fs.errors.ResourceInvalidError:
            parts = url.rsplit('/', 1)
            wrapper = get_fs_wrapper(parts[0], credentials=dict(
                username=username, password=password),
                context=self)
            wrapper.__leaf__ = True
            wrapper.__leaf_filename__ = parts[1]
            return wrapper
        except fs.errors.RemoteConnectionError as e:
            #  LOG.error(u'Error accessing {}::{}::{}'.format(
            #    self.absolute_url(),
            #    url,
            #   self.REQUEST.get('HTTP_USER_AGENT')),
            #    exc_info=True)
            exc = RuntimeError(url)
            exc.url = url
            raise exc

        except RequiresAuthorizationError as e:
            if e.authorization_url:
                self.plone_utils.addPortalMessage(
                    _(u'You need to authorize the connector first. Visit {}'.format(e.authorization_url)))
            raise

        except Exception as e:
            LOG.warn(u'Error accessing {}::{}::{}'.format(
                self.absolute_url(), url, self.REQUEST.get('HTTP_USER_AGENT')), exc_info=True)
            e.url = url
            raise e

    # aliases
    webdav_handle = get_handle

    def set_connector_url(self, value):
        self.connector_url = value

    def get_connector_url(self):
        return self.connector_url

    webdav_url = property(get_connector_url, set_connector_url)

    def set_connector_username(self, value):
        self.connector_username = value

    def get_connector_username(self):
        return self.connector_username

    webdav_username = property(get_connector_username, set_connector_username)

    def set_connector_password(self, value):
        self.connector_password = value

    def get_connector_password(self):
        return self.connector_password

    webdav_password = property(get_connector_password, set_connector_password)

    def set_connector_subpath(self, value):
        self.connector_subpath = value

    def get_connector_subpath(self):
        return self.connector_subpath

    webdav_subpath = property(get_connector_subpath, set_connector_subpath)
