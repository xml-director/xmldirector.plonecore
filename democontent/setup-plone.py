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

#uf._doChangeUser('admin', admin_pw, ('Manager',), ())
newSecurityManager(None, user.__of__(uf))

if 'xml-director' in app.objectIds():
    app.manage_delObjects('xml-director')

addPloneSite(app, 'xml-director', create_userfolder=True, extension_ids=['plonetheme.sunburst:default', 'xmldirector.plonecore:democontent'])
site = app['xml-director']
pr = site.portal_registration
pr.addMember('demo', 'demo', roles=('Site Administrator',))

registry = getUtility(IRegistry)
settings = registry.forInterface(IWebdavSettings)
settings.webdav_url = u'http://localhost:8080/exist/webdav/db'
settings.webdav_username = u'admin'
settings.webdav_password = u'admin'

folder = plone.api.content.create(type='Folder', container=site, id='shakespeare', title='Shakespeare XML')
import_dir = os.path.join(os.getcwd(), 'democontent', 'shakespeare')
for name in os.listdir(import_dir):
    fname = os.path.join(import_dir, name)
    dok = plone.api.content.create(
            type='xmldirector.plonecore.xmldocument',
            container=folder,
            id=name,
            title=name)
    with open(fname, 'rb') as fp:
        print fname
        xml = unicode(fp.read(), 'utf8')
        dok.xml_set('xml_content', xml)
    dok.reindexObject()

transaction.commit()
