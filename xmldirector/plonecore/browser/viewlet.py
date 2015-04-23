# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


from plone.app.layout.viewlets import ViewletBase
from xmldirector.plonecore.dx import util
from xmldirector.plonecore.locking import LockManager
from xmldirector.plonecore.dx.util import get_storage_path
from xmldirector.plonecore.logger import LOG


class Debug(ViewletBase):

    def info(self):

        if not util.is_xml_content(self.context):
            return

        storage_path = get_storage_path(self.context)
        path = '{}/xml_content.xml'.format(storage_path)
        LM = LockManager(self.context)

        try:
            lock_info = LM.get_lock(path)
        except Exception as e:
            LOG.debug(e)
            lock_info = None

        return dict(lock_info=lock_info,
                    storage_key=util.get_storage_key(self.context),
                    storage_path=util.get_storage_path(self.context))
