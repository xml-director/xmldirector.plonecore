# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from xmldirector.plonecore.dx import util
from xmldirector.plonecore.dx.xpath_field import get_all_xml_fields
from xmldirector.plonecore.dx.dexterity_base import xml_get
from xmldirector.plonecore.dx.dexterity_base import xml_set
from xmldirector.plonecore.interfaces import IWebdavSettings
from xmldirector.plonecore.interfaces import IWebdavHandle


def removal_handler(obj, event):
    """ Remove related XML content if a Dexterity content object
        is being deleted.
    """

    if not util.is_xml_content(event.object):
        return

    handle = getUtility(IWebdavHandle).webdav_handle()
    storage_dir = util.get_storage_path(event.object)
    storage_parent_dir = util.get_storage_path_parent(event.object)
    if handle.exists(storage_dir):
        handle.removedir(storage_dir, False, True)
    if handle.exists(storage_parent_dir) and handle.isdirempty(storage_parent_dir):
        handle.removedir(storage_parent_dir, False, True)


def copied_handler(obj, event):
    """ Copy XML resources to new object """

    # original and copied Dexterity object
    copied = event.object
    original = event.original

    # Is this Dexterity content object related to XML resources?
    if not util.is_xml_content(copied):
        return

    # create a new storage id
    if util.get_storage_key(original) == util.get_storage_key(copied):
        util.new_storage_key(copied)

        # an copy over XML content from original content object
        handle = getUtility(IWebdavHandle).webdav_handle()
        storage_dir_original = util.get_storage_path(original)
        storage_dir_copied = util.get_storage_path(copied)
        storage_dir_copied_parent = util.get_storage_path_parent(copied)
        handle.makedir(storage_dir_copied_parent, True, True)
        handle.copydir(storage_dir_original, storage_dir_copied)


#def version_handler(obj, event):
#    """ Copy XML resources to new object """
#
#    # Is this Dexterity content object related to XML resources?
#    if not util.is_xml_content(event.object):
#        return
#
#    return
