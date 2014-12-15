import os
import plone.api
import grampg
import transaction
from Products.CMFPlone.factory import addPloneSite
from AccessControl.SecurityManagement import newSecurityManager
from xmldirector.plonecore.interfaces import IWebdavSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

admin_pw = grampg.PasswordGenerator().of().between(100, 200, 'letters').done().generate()

uf = app.acl_users
user = uf.getUser('admin')

uf._doChangeUser('admin', admin_pw, ('Manager',), ())
newSecurityManager(None, user.__of__(uf))

if 'xml-director' in app.objectIds():
    app.manage_delObjects('xml-director')

addPloneSite(app, 'xml-director', create_userfolder=True, extension_ids=['plonetheme.sunburst:default', 'xmldirector.plonecore:democontent'])
plone = app['xml-director']
pr = plone.portal_registration
pr.addMember('demo', 'demo', roles=('Site Administrator',))

registry = getUtility(IRegistry)
settings = registry.forInterface(IWebdavSettings)
settings.webdav_url = u'http://localhost:8080/exist/webdav/db'
settings.webdav_username = u'admin'
settings.webdav_password = u'exist'

folder = plone.api.content.create('Folder', container=plone, id='shakespeare', title='Shakespeare XML')
import_dir = os.path.join(os.path.dirname(__file__), 'shakespeare')
for name in os.listdir(import_dir):
    fname = os.path.join(import_dir, name)
    dok = plone.api.content.create(
            type='xmldirector.plonecore.xmldocument',
            container=folder,
            id=name,
            title=name)
    with open(fname, 'rb') as fp:
        dok.set_xml('xml_content', fp.read())
    dok.reindexObject()






transaction.commit()
