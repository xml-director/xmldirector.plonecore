# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import uuid
import unittest2
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

from xmldirector.plonecore.interfaces import IWebdavSettings
from xmldirector.plonecore.davfs import DAVFSWrapper as DAVFS

import xmldirector.plonecore
import plone.app.dexterity


WEBDAV_URL = os.environ.get(
    'WEBDAV_URL', 'http://localhost:6080/exist/webdav/db')
WEBDAV_USERNAME = os.environ.get('WEBDAV_USERNAME', 'admin')
WEBDAV_PASSWORD = os.environ.get('WEBDAV_PASSWORD', 'admin')

os.environ['TESTING'] = '1'


class PolicyFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        #        xmlconfig.file('meta.zcml', z3c.jbot, context=configurationContext)

        for mod in [plone.app.dexterity,
                    xmldirector.plonecore,
                    ]:
            xmlconfig.file('configure.zcml', mod, context=configurationContext)

        # Install product and call its initialize() function
#        z2.installProduct(app, 'eteaching.policy')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'xmldirector.plonecore:testing')
        portal.acl_users.userFolderAddUser('god', 'dummy', ['Manager'], [])
        portal.acl_users.userFolderAddUser('god2', 'dummy', ['Manager'], [])
        setRoles(portal, 'god', ['Manager'])
        setRoles(portal, 'god2', ['Manager'])
        login(portal, 'god')

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IWebdavSettings)
        settings.webdav_username = unicode(WEBDAV_USERNAME)
        settings.webdav_password = unicode(WEBDAV_PASSWORD)
        settings.webdav_url = unicode(WEBDAV_URL)
        self.testing_directory = settings.webdav_dexterity_subpath = u'testing-dexterity-{}'.format(
            uuid.uuid4())

        self.connector = plone.api.content.create(
            container=portal,
            type='xmldirector.plonecore.connector',
            id='connector')

    def tearDownZope(self, app):

        handle = DAVFS(WEBDAV_URL, credentials=dict(username=WEBDAV_USERNAME,
                                                    password=WEBDAV_PASSWORD))
        if handle.exists(self.testing_directory):
            handle.removedir(
                self.testing_directory, recursive=True, force=True)
        z2.uninstallProduct(app, 'xmldirector.plonecore')


POLICY_FIXTURE = PolicyFixture()
POLICY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(POLICY_FIXTURE,), name='PolicyFixture:Integration')


class TestBase(unittest2.TestCase):

    layer = POLICY_INTEGRATION_TESTING

    @property
    def portal(self):
        return self.layer['portal']

    def login(self, uid='god'):
        """ Login as manager """
        user = self.portal.acl_users.getUser(uid)
        newSecurityManager(None, user.__of__(self.portal.acl_users))
