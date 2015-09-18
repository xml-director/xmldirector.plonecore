# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


from Products.Five.browser import BrowserView
from xmldirector.plonecore.locking import LockManager
from xmldirector.plonecore.dx.util import get_storage_path


class Lock(BrowserView):

    def lock(self):

        storage_path = get_storage_path(self.context)

        LM = LockManager(self.context)
        path = '{}/xml_content.xml'.format(storage_path)
        lock_info = LM.lock(path, mode='shared')
        return lock_info

    def unlock(self):

        storage_path = get_storage_path(self.context)
        LM = LockManager(self.context)
        path = '{}/xml_content.xml'.format(storage_path)
        LM.unlock(path, token=None)
        return 'unlocked'
