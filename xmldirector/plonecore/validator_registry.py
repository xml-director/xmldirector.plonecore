# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import os
import fs.opener
import datetime
import operator
import lxml.etree
import lxml.isoschematron
from zope.interface import implements
from xmldirector.plonecore.interfaces import IValidatorRegistry
from xmldirector.plonecore.logger import LOG

# The schema registry holds references for the following XML validation
# methods:
#
# - XML Schema (.xsd)
# - Document Type Definitions (DTD) (.dtd)
# - RelaxNG schema (.rng)
# - Schematron (.sch)

# All entries are stored internally as a tuple (family, name).  ``family``
# could be used to represent a project, a customer etc.  and ``name`` would
# represent the name of the DTD or schema Both ``family`` and ``name`` are
# completey arbitrary.


class ValidatorRegistry(object):
    """ A registry for XML schemas and DTDs """

    implements(IValidatorRegistry)

    registry = {}

    def parse_folder(self, family, directory):
        """ Parse a given folder for XML schema files (.xsd) or
            DTD files (.dtd).
        """

        if directory.startswith('/'):
            directory = 'file://' + directory

        try:
            handle = fs.opener.fsopendir(directory)
        except Exception as e:
            raise IOError(u'Directory "{}" does not exist ({})'.format(directory, e))

        for name in handle.listdir():
            fullname = os.path.join(directory, name)
            base, ext = os.path.splitext(name)

            key = '{}::{}'.format(family, name)
            if ext == '.dtd':
                with handle.open(name, 'rb') as fp:
                    validator = lxml.etree.DTD(fp)
                    validator_type = 'DTD'
            elif ext == '.xsd':
                with handle.open(name, 'rb') as fp:
                    schema_doc = lxml.etree.XML(fp.read())
                    validator = lxml.etree.XMLSchema(schema_doc)
                    validator_type = 'XSD'
            elif ext == '.rng':
                with handle.open(name, 'rb') as fp:
                    relaxng_doc = lxml.etree.XML(fp.read())
                    validator = lxml.etree.RelaxNG(relaxng_doc)
                    validator_type = 'RELAXNG'
            elif ext == '.sch':
                with handle.open(name, 'rb') as fp:
                    relaxng_doc = lxml.etree.XML(fp.read())
                    validator = lxml.isoschematron.Schematron(relaxng_doc)
                    validator_type = 'SCHEMATRON'
            else:
                continue

            if key in self.registry:
                raise ValueError('{} already registered'.format(key))

            self.registry[key] = dict(
                family=family,
                name=name,
                validation=validator,
                path=fullname,
                info=handle.getinfo(name),
                type=validator_type,
                registered=datetime.datetime.utcnow())
            LOG.info('Registered ({}, {})'.format(key, fullname))

    def get_schema(self, family, name):
        """ Return a pre-validator DTD/schema/RelaxNG/Schematron """

        key = '{}::{}'.format(family, name)
        if key not in self.registry:
            raise ValueError(
                'Schema/DTD {}/{} not registered'.format(family, name))
        return self.registry[key]['validation']

    def get_validator(self, family, name):
        """ Return a wrapped Validator instance for the given family + name """
        schema = self.get_schema(family, name)
        return Validator(schema)

    def _convert_key(self, name_or_tuple):
        if isinstance(name_or_tuple, tuple):
            return name_or_tuple
        return name_or_tuple.split('::')

    def __getitem__(self, name_or_tuple):
        return self.get_schema(*self._convert_key(name_or_tuple))

    def __contains__(self, name_or_tuple):
        return self.get_schema(*self._convert_key(name_or_tuple))

    def clear(self):
        """ Remove all entries """
        self.registry.clear()

    def __len__(self):
        """ Return number of registered transformations """
        return len(self.registry)

    def entries(self):
        """ All entries as sorted list """
        result = self.registry.values()
        return sorted(result, key=operator.itemgetter('family', 'name'))


ValidatorRegistryUtility = ValidatorRegistry()


class ValidationResult(object):
    """ Encapsulates DTD/schema validation results """

    def __init__(self, errors=[]):
        self.errors = errors

    def __nonzero__(self):
        return not self.errors

    def __str__(self):
        return '{}, errors: {}'.format(self.__class__, self.errors)


class Validator(object):
    """ Encapsulates a schema validator """

    def __init__(self, schema):
        self.schema = schema

    def validate(self, xml):

        if isinstance(xml, basestring):
            try:
                root = lxml.etree.fromstring(xml)
            except lxml.etree.XMLSyntaxError as e:
                return ValidationResult([u'Invalid XML ({})'.format(e)])

        elif isinstance(xml, lxml.etree.Element):
            root = xml
        else:
            raise TypeError('Unsupported type {}'.format(type(xml)))

        validation_result = self.schema.validate(root)
        if not validation_result:
            return ValidationResult([self.schema.error_log])
        else:
            return ValidationResult()
