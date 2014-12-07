
import uuid
from five import grok
import plone.api
from fs.contrib.davfs import DAVFS
from plone.registry.interfaces import IRegistry
from zopyx.existdb.interfaces import IExistDBSettings
from zope.lifecycleevent import IObjectCopiedEvent
from zope.component import getUtility


@grok.subscribe(IObjectCopiedEvent)
def handler(e):
    if IObjectCopiedEvent.providedBy(e):

        current = e.object
        old = e.original
        
        try:
            old.__xml_storage_id_
        except AttributeError:
            return

        if str(current.__xml_storage_id__) == str(old.__xml_storage_id__):
            current.__xml_storage_id__ = uuid.uuid4()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IExistDBSettings)

        url = settings.existdb_url
        url = '{}/exist/webdav/db'.format(url)
        username = settings.existdb_username
        password = settings.existdb_password

        handle = DAVFS(url, credentials=dict(username=username,
                                             password=password))

        plone_uid = plone.api.portal.get().getId()
        storage_dir_old = 'plone-data/{}/{}'.format(plone_uid, old.__xml_storage_id__)
        storage_dir_new = 'plone-data/{}/{}'.format(plone_uid, current.__xml_storage_id__)

        print storage_dir_old
        print storage_dir_new
        handle.copydir(storage_dir_old, storage_dir_new)

