# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import os
import operator
import tempfile
import defusedxml.lxml
import lxml.etree
import fs.opener
import datetime
import shutil
import pkg_resources

from zope.interface import implements
from zope.interface import Interface
from xmldirector.plonecore.interfaces import ITransformerRegistry
from xmldirector.plonecore.logger import LOG
from xmldirector.plonecore.util import runcmd


class ITransformerWrapper(Interface):

    """ Marker interface for transformer wrappers """

    def __init__(transformer):
        pass

    def __call__(root, conversion_context):
        pass


# The transformer registry stores arbitrary XML transformations.
# A transformer is identifed through a tuple (family, transformer_name).
# ``family`` # could be used to represent a project, a customer etc.  and
# ``transformer_name`` would represent the name of the transformation.
# The registry allows to register different transformer implementation like
# XSLT1 transformations, Python methods etc.
# For each transformation type there must be an adapter implementing ITransformerWrapper
# which is the canonical API for chaining different transformations.


class XSLT1Wrapper(object):

    implements(ITransformerWrapper)

    def __init__(self, registry_entry):
        # ``transformer`` is the original transformer object
        self.entry = registry_entry

    def __call__(self, root, conversion_context):
        # ``root`` is parsed root node of the document to be transformed
        # as an lxml.etree.Element instance.
        # The ``conversion_context`` is a dict holding the current ``context`` object,
        # the current ``request`` object and the destination directory
        # ``destdir``.
        return self.entry['transform'](root)


class SaxonWrapper(object):

    """ A Saxon 9.6 wrapper for XSLT 2/3 transformations """

    implements(ITransformerWrapper)

    def __init__(self, registry_entry):
        self.entry = registry_entry

    def __call__(self, root, conversion_context):

        temp_d = tempfile.mkdtemp()

        # Store XML of node ``root`` and store it on the FS
        xml_in = os.path.join(temp_d, 'in.xml')
        with open(xml_in, 'wb') as fp:
            fp.write(lxml.etree.tostring(root, encoding='utf8'))

        # Store XSLT on the filesystem
        xslt_in = os.path.join(temp_d, 'in.xsl')
        with fs.opener.opener.open(self.entry['transform'], 'rb') as fp_in:
            with open(xslt_in, 'wb') as fp_out:
                fp_out.write(fp_in.read())

        # Output XML file
        xml_out = os.path.join(temp_d, 'out.xml')

        # Determine path to Saxon JAR file
        saxon_path = os.path.join(pkg_resources.get_distribution(
            'xmldirector.plonecore').location, 'xmldirector', 'plonecore', 'transformations', 'saxon', 'saxon9he.jar')

        cmd = 'java -jar "{}" -s:"{}" -xsl:"{}" -o:"{}"'.format(
            saxon_path, xml_in, xslt_in, xml_out)
        status, output = runcmd(cmd)
        with open(xml_out, 'rb') as fp:
            xml_out = fp.read()

        # house keeping
        shutil.rmtree(temp_d)
        return defusedxml.lxml.fromstring(xml_out)


class TransformerRegistry(object):

    implements(ITransformerRegistry)

    registry = {}

    def register_transformation(self, family, transformer_name, transformer_path, transformer_type='XSLT1'):
        """ Register a Transformation as tuple (``family``, ``transformer_name``).
            ``transformer_path`` is either an URI to the related transformation file on the filesystem (XSLT1)
            or a Python function implementing the IWrapper.

            Supported ``transformer_type``s so far: 'XSLT1', 'python'
        """

        if transformer_type == 'python':
            # ``transformer_path`` is Python function here
            transform = transformer_path
            method_filename = transform.func_code.co_filename
            transformer_path = '{}(), {}'.format(
                transformer_path.func_name, transformer_path.func_code.co_filename)
            dir_handle = fs.opener.fsopendir('{}/..'.format(method_filename))
            info = dir_handle.getinfo(os.path.basename(method_filename))

        elif transformer_type in ('XSLT1', 'XSLT2', 'XSLT3'):

            try:
                handle = fs.opener.opener.open(transformer_path)
            except Exception as e:
                raise ValueError(
                    'Transformation {}/{} not found ({}, {})'.format(family, transformer_name, transformer_path, e))

            with fs.opener.opener.open(transformer_path, 'rb') as fp:

                if transformer_path.startswith('/'):
                    transformer_path = 'file://' + transformer_path

                dir_handle = fs.opener.fsopendir('{}/..'.format(handle.name))
                info = dir_handle.getinfo(os.path.basename(handle.name))

                try:
                    xslt = lxml.etree.XML(fp.read())
                except lxml.etree.XMLSyntaxError as e:
                    raise ValueError(
                        'Transformation {}/{} could not be parsed ({}, {})'.format(
                            family,
                            transformer_name,
                            e,
                            transformer_path))

                xslt_version = xslt.attrib.get('version', '1.0')
                if xslt_version[0] != transformer_type[-1]:
                    raise ValueError('Stylesheet version "{}" does not match specified transformer_type "{}"'.format(
                        xslt_version, transformer_type))

                if transformer_type == 'XSLT1':
                    try:
                        transform = lxml.etree.XSLT(xslt)
                    except lxml.etree.XSLTParseError as e:
                        raise ValueError(
                            'Transformation {}/{} could not be parsed ({}, {})'.format(
                                family,
                                transformer_name,
                                e,
                                transformer_path))
                else:
                    # XSLT2+3
                    transform = transformer_path

        else:
            raise ValueError(
                u'Unsupported transformer type "{}"'.format(transformer_type))

        key = '{}::{}'.format(family, transformer_name)
        if key in self.registry:
            raise ValueError(
                'Transformation {}/{} already registered'.format(family, transformer_name))

        self.registry[key] = dict(
            transform=transform,
            path=transformer_path,
            type=transformer_type,
            family=family,
            name=transformer_name,
            info=info,
            registered=datetime.datetime.utcnow())

        LOG.info(
            'Transformer registered ({}, {})'.format(key, transformer_path))

    def entries(self):
        """ Return all entries of the registry sorted by family + name """
        result = self.registry.values()
        return sorted(result, key=operator.itemgetter('family', 'name'))

    def clear(self):
        """ Remove all entries """
        self.registry.clear()

    def __len__(self):
        """ Return number of registered transformations """
        return len(self.registry)

    def get_transformation(self, family, transformer_name):
        """ Return a transformer by (family, transformer_name) """

        key = '{}::{}'.format(family, transformer_name)
        if key not in self.registry:
            raise ValueError(
                'Transformation {}/{} not registered'.format(family, transformer_name))
        d = self.registry[key]
        if d['type'] == 'python':
            return d['transform']
        elif d['type'] == 'XSLT1':
            return XSLT1Wrapper(d)
        elif d['type'] in ('XSLT2', 'XSLT3'):
            return SaxonWrapper(d)


TransformerRegistryUtility = TransformerRegistry()
