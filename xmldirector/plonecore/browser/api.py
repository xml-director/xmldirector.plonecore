# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import json
import defusedxml.lxml
import lxml.etree
import urllib.parse
import requests
from requests.auth import HTTPBasicAuth

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from zExceptions import Forbidden
from zExceptions import NotFound

from xmldirector.plonecore.interfaces import IConnectorSettings


class APIError(Exception):
    pass


class API(BrowserView):

    def generic_query(self, script_path='all-documents',
                      output_format='json', deserialize_json=False, **kw):
        """ Public query API for calling xquery scripts through RESTXQ.
            The related xquery script must expose is functionality through
            http://host:port/exist/restxq/<script_path>.<output_format>.
            The result is then returned as text (html, xml) or deserialized
            JSON data structure.
            Note that <script_path> must start with '/db/' or 'db/'.
        """

        if self.context and not self.context.api_enabled:
            raise Forbidden('API not enabled')

        if output_format not in ('json', 'xml', 'html'):
            raise NotFound(
                'Unsupported output format "{}"'.format(output_format))

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IConnectorSettings)
        pr = urllib.parse.urlparse(settings.connector_url)
        url = '{}://{}/exist/restxq/{}.{}'.format(
            pr.scheme, pr.netloc, script_path, output_format)

        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        result = session.get(url,
                             auth=HTTPBasicAuth(settings.connector_username,
                                                settings.connector_password or ''),
                             params=kw)
        if result.status_code != 200:
            raise APIError(
                'eXist-db return an response with HTTP code {} for {}'.format(result.status_code, url))

        if output_format == 'json':
            data = result.json()
            if deserialize_json:
                # called internally (and not through the web)
                data = result.json()
                return data
            else:
                data = result.text
                self.request.response.setHeader(
                    'content-type', 'application/json')
                self.request.response.setHeader('content-length', len(data))
                return data
        else:
            data = result.text
            self.request.response.setHeader(
                'content-type', 'text/{}'.format(output_format))
            self.request.response.setHeader('content-length', len(data))
            return data


class Validation(BrowserView):

    def validate(self, xml):
        """ Perform server-side XML validation """

        if not xml.startswith('<?xml'):
            xml = unicode(xml, 'utf8')

        errors = []
        if xml:
            try:
                defusedxml.lxml.fromstring(xml)
            except lxml.etree.ParseError as e:
                errors.append(u'Parse error {}'.format(repr(e)))
        return json.dumps(errors)
