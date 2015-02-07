# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import os
import operator
import fs.opener
import datetime
import lxml.etree
from zope.interface import implements
from xmldirector.plonecore.interfaces import IXSLTRegistry
from xmldirector.plonecore.logger import LOG


# The XSLT registrie stores pre-compiled XSLT transformations as a dictionary
# where the keys are composed of a tuple (family, stylesheet_name).  ``family``
# could be used to represent a project, a customer etc.  and
# ``stylesheet_name`` would represent the name of the XSLT transformation.
# Both ``family`` and ``stylesheet_name`` are completey arbitrary.

class XSLTRegistry(object):

    implements(IXSLTRegistry)

    registry = {}

    def register_stylesheet(self, family, stylesheet_name, stylesheet_path):
        """ Register a Stylesheet as tuple (family, stylesheet_name) """

        if stylesheet_path.startswith('/'):
            stylesheet_path = 'file://' + stylesheet_path

        key = '{}::{}'.format(family, stylesheet_name)
        if key in self.registry:
            raise ValueError(
                'Stylesheet {}/{} already registered'.format(family, stylesheet_name))


        try:
            handle = fs.opener.opener.open(stylesheet_path)
        except Exception as e:
            raise ValueError(
                'Stylesheet {}/{} not found ({}, {})'.format(family, stylesheet_name, stylesheet_path, e))

        dir_handle = fs.opener.fsopendir('{}/..'.format(handle.name))
        info = dir_handle.getinfo(os.path.basename(handle.name))

        with fs.opener.opener.open(stylesheet_path, 'rb') as fp:
            try:
                xslt = lxml.etree.XML(fp.read())
            except lxml.etree.XMLSyntaxError as e:
                raise ValueError(
                    'Stylesheet {}/{} could not be parsed ({}, {})'.format(family, stylesheet_name, e, stylesheet_path))

            try:
                transform = lxml.etree.XSLT(xslt)
            except lxml.etree.XSLTParseError as e:
                raise ValueError(
                    'Stylesheet {}/{} could not be parsed ({}, {})'.format(family, stylesheet_name, e, stylesheet_path))
        
            self.registry[key] = dict(
                transform=transform,
                path=stylesheet_path,
                type='XSLT',
                family=family,
                name=stylesheet_name,
                info=info,
                registered=datetime.datetime.utcnow())
            LOG.info('XSLT registered ({}, {})'.format(key, stylesheet_path))

    def entries(self):
        result = self.registry.values()
        return sorted(result, key=operator.itemgetter('family', 'name'))

    def get_stylesheet(self, family, stylesheet_name):
        """ Return a pre-compiled XSLT transformation by (family, stylesheet_name) """

        key = '{}::{}'.format(family, stylesheet_name)
        if key not in self.registry:
            raise ValueError(
                'Stylesheet {}/{} not registered'.format(family, stylesheet_name))
        return self.registry[key]['transform']

    def clear(self):
        """ Remove all entries """
        self.registry.clear()

    def __len__(self):
        """ Return number of registered transformations """
        return len(self.registry)


XSLTRegistryUtility = XSLTRegistry()
