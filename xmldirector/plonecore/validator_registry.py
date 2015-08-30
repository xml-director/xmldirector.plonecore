# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import os
import time
import fs.opener
import datetime
import operator
import defusedxml.lxml
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

    def parse_folder(self, family, directory, version_suffix=None):
        """ Parse a given folder for XML schema files (.xsd) or
            DTD files (.dtd).
        """

        if directory.startswith('/'):
            directory = 'file://' + directory

        try:
            handle = fs.opener.fsopendir(directory)
        except Exception as e:
            raise IOError(
                u'Directory "{}" does not exist ({})'.format(directory, e))

        for name in handle.listdir():
            fullname = os.path.join(directory, name)
            LOG.info(u'Parsing "{}"'.format(fullname))
            base, ext = os.path.splitext(name)

            registered_name = name
            if version_suffix:
                basename, ext = os.path.splitext(name)
                registered_name = '{}-{}{}'.format(basename,
                                                   version_suffix, ext)

            key = '{}::{}'.format(family, registered_name)
            ts = time.time()
            if ext == '.dtd':
                with handle.open(name, 'rb') as fp:
                    validator = lxml.etree.DTD(fp)
                    validator_type = 'DTD'
            elif ext == '.xsd':
                with handle.open(name, 'rb') as fp:
                    try:
                        schema_doc = lxml.etree.XML(fp.read())
                        validator = lxml.etree.XMLSchema(schema_doc)
                    except Exception as e:
                        LOG.error(u'Unable to parse XML Schema ({})'.format(e), exc_info=True)
                        continue
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

            duration = time.time() - ts

            self.registry[key] = dict(
                family=family,
                name=registered_name,
                validation=validator,
                path=fullname,
                info=handle.getinfo(name),
                duration=duration,
                type=validator_type,
                registered=datetime.datetime.utcnow())
            if duration > 3:
                LOG.warn(
                    'Slow loading/parsing of ({}, {}), duration: {:0.3f} seconds'.format(key, fullname, duration))
            LOG.info('Registered ({}, {}), duration: {:0.3f} seconds'.format(
                key, fullname, duration))

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
        return Validator(schema, family, name)

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

    def __init__(self, errors=None, validator=None):
        self.errors = errors or []
        self.validator = validator

    def __nonzero__(self):
        return not self.errors

    def __str__(self):
        return '{}, validator: {}, errors: {}'.format(self.__class__, self.validator, self.errors)


class Validator(object):

    """ Encapsulates a schema validator """

    def __init__(self, schema, family, name):
        self.schema = schema
        self.family = family
        self.name = name

    def validate(self, xml):

        if isinstance(xml, basestring):
            try:
                root = defusedxml.lxml.fromstring(xml)
            except lxml.etree.XMLSyntaxError as e:
                return ValidationResult([u'Invalid XML ({})'.format(e)])

        elif isinstance(xml, lxml.etree._Element):
            root = xml

        else:
            raise TypeError('Unsupported type {}'.format(type(xml)))

        validation_result = self.schema.validate(root)
        validator_key = '{}::{}'.format(self.family, self.name)
        if not validation_result:
            return ValidationResult(errors=[self.schema.error_log], validator=validator_key)
        else:
            return ValidationResult(validator=validator_key)
