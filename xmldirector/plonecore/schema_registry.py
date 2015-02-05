# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import os
import datetime
import lxml.etree
from zope.interface import implements
from xmldirector.plonecore.interfaces import ISchemaRegistry
from xmldirector.plonecore.logger import LOG


class SchemaRegistry(object):

    implements(ISchemaRegistry)

    schema_registry = {}

    def parse_folder(self, family, directory):
        
        if not os.path.exists(directory):
            raise IOError(u'Schema/DTD directory "{}" does not exist'.format(directory))

        for name in os.listdir(directory):
            fullname = os.path.join(directory, name)
            base, ext = os.path.splitext(name)

            key = '{}::{}'.format(family, name)
            if ext == '.dtd':
                with open(fullname, 'rb') as fp:
                    validator = lxml.etree.DTD(fp)
            elif ext == '.xsd':
                with open(fullname, 'rb') as fp:
                    schema_doc = lxml.etree(fp)
                    validator = lxml.etree.XMLSchema(schema_doc)
            else:
                continue

            if key in self.schema_registry:
                raise ValueError('{} already registered'.format(key))

            self.schema_registry[key] = dict(
                validation=validator,
                path=fullname,
                registered=datetime.datetime.utcnow())
            LOG.info('Schema/DTD registered ({}, {})'.format(key, fullname))

    def get_schema(self, family, name):
        """ Return a pre-validator DTD/schema """

        key = '{}::{}'.format(family, name)
        if key not in self.schema_registry:
            raise ValueError(
                'Schema/DTD {}/{} not registered'.format(family, name))
        return self.schema_registry[key]['validation']

    def clear(self):
        """ Remove all entries """
        self.schema_registry.clear()

    def __len__(self):
        """ Return number of registered transformations """
        return len(self.schema_registry)


SchemaRegistryUtility = SchemaRegistry()
