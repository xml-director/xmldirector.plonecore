# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import uuid
import unittest
import plone.api
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import setRoles
from plone.app.testing import login
from plone.testing import z2
from plone.registry.interfaces import IRegistry

from zope.component import getUtility
from zope.configuration import xmlconfig
from AccessControl.SecurityManagement import newSecurityManager

from xmldirector.plonecore.interfaces import IConnectorSettings
from xmldirector.plonecore.fswrapper import get_fs_wrapper
from xmldirector.plonecore.logger import LOG

import xmldirector.plonecore
import zopyx.plone.persistentlogger
import plone.app.dexterity


CONNECTOR_URL = os.environ.get(
    'CONNECTOR_URL', 'http://localhost:6080/exist/webdav/db')
CONNECTOR_USERNAME = os.environ.get('CONNECTOR_USERNAME', 'admin')
CONNECTOR_PASSWORD = os.environ.get('CONNECTOR_PASSWORD', 'admin')

os.environ['TESTING'] = '1'


class PolicyFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        #        xmlconfig.file('meta.zcml', z3c.jbot, context=configurationContext)

        for mod in [plone.app.dexterity,
                    xmldirector.plonecore,
                    zopyx.plone.persistentlogger,
                    ]:
            xmlconfig.file('configure.zcml', mod, context=configurationContext)

        # Install product and call its initialize() function
#        z2.installProduct(app, 'eteaching.policy')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'zopyx.plone.persistentlogger:default')
        applyProfile(portal, 'xmldirector.plonecore:testing')
        portal.acl_users.userFolderAddUser('god', 'dummy', ['Manager'], [])
        portal.acl_users.userFolderAddUser('god2', 'dummy', ['Manager'], [])
        setRoles(portal, 'god', ['Manager'])
        setRoles(portal, 'god2', ['Manager'])
        login(portal, 'god')

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IConnectorSettings)
        settings.connector_username = unicode(CONNECTOR_USERNAME)
        settings.connector_password = unicode(CONNECTOR_PASSWORD)
        settings.connector_url = unicode(CONNECTOR_URL)
        self.testing_directory = settings.connector_dexterity_subpath = u'testing-dexterity-{}'.format(
            uuid.uuid4())

        handle = get_fs_wrapper(CONNECTOR_URL, credentials=dict(username=CONNECTOR_USERNAME,
                                                             password=CONNECTOR_PASSWORD))
        if not handle.exists(self.testing_directory):
            handle.makedir(self.testing_directory)

        self.connector = plone.api.content.create(
            container=portal,
            type='xmldirector.plonecore.connector',
            id='connector')

    def tearDownZope(self, app):

        handle = get_fs_wrapper(CONNECTOR_URL, credentials=dict(username=CONNECTOR_USERNAME,
                                                             password=CONNECTOR_PASSWORD))
        if handle.exists(self.testing_directory):
            try:
                handle.removedir(
                    self.testing_directory, recursive=True, force=True)
            except Exception as e:
                LOG.error('tearDownZope() failed ({})'.format(e))
        z2.uninstallProduct(app, 'xmldirector.plonecore')


POLICY_FIXTURE = PolicyFixture()
POLICY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(POLICY_FIXTURE,), name='PolicyFixture:Integration')


class TestBase(unittest.TestCase):

    layer = POLICY_INTEGRATION_TESTING

    @property
    def portal(self):
        return self.layer['portal']

    def login(self, uid='god'):
        """ Login as manager """
        user = self.portal.acl_users.getUser(uid)
        newSecurityManager(None, user.__of__(self.portal.acl_users))
