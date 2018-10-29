# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import os
import sys
import pkg_resources

from xmldirector.plonecore.logger import LOG


__import__('pkg_resources').declare_namespace(__name__)


# Check filesystem encoding
fs_enc = sys.getfilesystemencoding()
if fs_enc.lower() not in ('utf8', 'utf-8'):
    LOG.error('Filesystem encoding should be UTF-8, not {}'.format(fs_enc))


# import patches only for Plone 5
dist = pkg_resources.get_distribution('Products.CMFPlone')
if dist.version.startswith('5'):
    import patches
    LOG.info('Applied patched for Plone 5')
