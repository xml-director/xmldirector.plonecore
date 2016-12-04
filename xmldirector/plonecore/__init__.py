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

# check minimal versions
for mod, min_version in [('lxml', [3, 4])]:
    dist = pkg_resources.get_distribution('lxml')
    try:
        dist_version = map(int, dist.parsed_version[:-1])
    except ValueError:
        raise ValueError('Unable to parse version {}:{}'.format(
            mod, dist.parsed_version))
    if not min_version <= dist_version:
        min_version_s = '.'.join(map(str, min_version))
        raise RuntimeError('xmldirector.plonecore requires module {} in version {} or higher (installed: {})'.format(
            mod, min_version_s, dist.version))


# Check filesystem encoding
fs_enc = sys.getfilesystemencoding()
if fs_enc.lower() not in ('utf8', 'utf-8'):
    LOG.error('Filesystem encoding should be UTF-8, not {}'.format(fs_enc))


# import patches only for Plone 5
dist = pkg_resources.get_distribution('Products.CMFPlone')
if dist.version.startswith('5'):
    import patches
    LOG.info('Applied patched for Plone 5')
