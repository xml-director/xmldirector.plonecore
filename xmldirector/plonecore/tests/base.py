# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
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
from xmldirector.plonecore.interfaces import IWebdavSettings
from AccessControl.SecurityManagement import newSecurityManager

import xmldirector.plonecore
import plone.app.dexterity


EXIST_DB_URL = os.environ.get('EXIST_DB_URL', 'http://localhost:6080/exist/webdav/db')
EXIST_DB_USERNAME = os.environ.get('EXIST_DB_USERNAME', 'admin')
EXIST_DB_PASSWORD = os.environ.get('EXIST_DB_PASSWORD', 'admin')


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
        applyProfile(portal, 'xmldirector.plonecore:default')
        portal.acl_users.userFolderAddUser('god', 'dummy', ['Manager'], [])
        setRoles(portal, 'god', ['Manager'])
        portal.acl_users.userFolderAddUser('ppr', 'dummy', ['PPR'], [])
        setRoles(portal, 'ppr', ['Member', 'PPR'])
        portal.acl_users.userFolderAddUser('member', 'dummy', ['Member'], [])
        setRoles(portal, 'member', ['Member'])
        login(portal, 'god')

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IWebdavSettings)
        settings.webdav_username = unicode(EXIST_DB_USERNAME)
        settings.webdav_password = unicode(EXIST_DB_PASSWORD)
        settings.webdav_url = unicode(EXIST_DB_URL)

        self.connector = plone.api.content.create(
            container=portal,
            type='xmldirector.plonecore.connector',
            id='connector')

    def tearDownZope(self, app):
        # Uninstall product
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