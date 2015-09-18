# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import time
import tempfile
import defusedxml.lxml
import lxml.etree

from zope.component import getUtility
from xmldirector.plonecore.interfaces import ITransformerRegistry
from xmldirector.plonecore.logger import LOG


class Transformer(object):

    def __init__(self, steps=None, context=None, destdir=None, transformer_registry=None, **params):
        """ Instantiate a new transformer chain with an arbitrary number of registered
            transformer steps. The chain ``steps`` is expressed as list of tuples
            [(family1, name1), (family2, name2), ...].
            ``context`` - the current context object in Plone.
            ``destdir`` - the work directory of the transformation
            ``transformer_registry`` - a custom transformer_registry instance (needed for tests only).
            ``params`` - an arbitrary data dict
        """

        if steps is None:
            steps = []
        self.steps = steps
        self.context = context
        self.destdir = destdir
        self.params = params
        self.transformer_registry = transformer_registry

    @property
    def registry(self):
        """ Return transformer registry """
        if self.transformer_registry:
            return self.transformer_registry
        return getUtility(ITransformerRegistry)

    def verify_steps(self):
        """ Verify all transformation steps before running the transformation """

        errors = list()
        for family, name in self.steps:
            try:
                self.registry.get_transformation(family, name)
            except ValueError:
                errors.append((family, name))
        if errors:
            raise ValueError('Unknown transformer steps: {}'.format(errors))

    def __call__(
            self,
            xml_or_node,
            input_encoding=None,
            output_encoding=unicode,
            return_fragment=None,
            pretty_print=False,
            debug=False):
        """ Run the transformation chain either on an XML document passed as ``xml_or_node`` parameter
            or as pre-parsed XML node (lxml.etree.Element). XML documents passed as string must be either of type
            unicode or you must specify an explicit ``input_encoding``. The result XML document is returned as
            unicode string unless a different ``output_encoding`` is specified. In order to return a subelement
            from the result XML document you can specify a tag name using ``return_fragment`` in order the subdocument
            starting with the given tag name.
        """

        # Check validness of the transformation chain first
        self.verify_steps()

        if debug:
            debug_dir = tempfile.mkdtemp(prefix='transformation_debug_')
            LOG.info('Transformation debug directory: {}'.format(debug_dir))

        # Convert XML string into a root node
        if isinstance(xml_or_node, basestring):
            if not isinstance(xml_or_node, unicode):
                if not input_encoding:
                    raise TypeError('Input data must be unicode')
                    xml_or_node = unicode(xml_or_node, input_encoding)
            root = defusedxml.lxml.fromstring(xml_or_node.strip())

        elif isinstance(xml_or_node, lxml.etree._Element):
            root = xml_or_node

        else:
            raise TypeError(
                u'Unsupported type {}'.format(xml_or_node.__class__))

        # run the transformation chain
        for step_no, step in enumerate(self.steps):
            family, name = step
            ts = time.time()
            transformer = self.registry.get_transformation(family, name)
            conversion_context = dict(context=self.context,
                                      request=getattr(
                                          self.context, 'REQUEST', None),
                                      destdir=self.destdir,
                                      )
            conversion_context.update(self.params)

            if debug:
                in_data = lxml.etree.tostring(root, encoding='utf8')
                in_data_fn = '{:02d}-{}-{}.in'.format(step_no, family, name)
                with open(os.path.join(debug_dir, in_data_fn), 'wb') as fp:
                    fp.write(in_data)

            # A transformation is allowed to return a new root node (None
            # otherwise).  The transformation chain will then continue in the
            # next transformation step with this new node.
            new_root = transformer(root, conversion_context=conversion_context)
            if new_root is not None:
                root = new_root

            if debug:
                out_data = lxml.etree.tostring(root, encoding='utf8')
                out_data_fn = '{:02d}-{}-{}.out'.format(step_no, family, name)
                with open(os.path.join(debug_dir, out_data_fn), 'wb') as fp:
                    fp.write(out_data)

            LOG.info('Transformation %-30s: %3.6f seconds' %
                     (name, time.time() - ts))

        # optional: return a fragment given by the top-level tag name
        return_node = root
        if return_fragment:
            node = root.find(return_fragment)
            if node is None:
                raise ValueError(
                    'No tag <{}> found in transformed document'.format(return_fragment))
            return_node = node

        if output_encoding == unicode:
            return lxml.etree.tostring(
                return_node,
                encoding=unicode,
                pretty_print=pretty_print)
        else:
            return lxml.etree.tostring(
                return_node.getroottree(),
                encoding=output_encoding,
                xml_declaration=True,
                pretty_print=pretty_print)
