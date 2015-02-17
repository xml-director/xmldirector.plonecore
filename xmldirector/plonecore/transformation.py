################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import time
import tempfile
import lxml.etree

from zope.component import getUtility
from xmldirector.plonecore.interfaces import ITransformerRegistry
from xmldirector.plonecore.logger import LOG


class Transformer(object):

    def __init__(self, steps=[], context=None, destdir=None, transformer_registry=None, **params):
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
        """ Verify all transformation steps """

        errors = list()
        for family, name in self.steps:
            try:
                self.registry.get_transformation(family, name)
            except ValueError:
                errors.append((family, name))
        if errors:
            raise ValueError('Unknown transformer steps: {}'.format(errors))

    def __call__(self, xml_or_node, input_encoding=None, output_encoding=unicode, return_fragment=None, debug=False):

        self.verify_steps()

        if debug:
            debug_dir = tempfile.mkdtemp(prefix='transformation_debug_')
            LOG.info('Transformation debug directory: {}'.format(debug_dir))

        if isinstance(xml_or_node, basestring):
            if not isinstance(xml_or_node, unicode):
                if not input_encoding:
                    raise TypeError('Input data must be unicode')
                    xml_or_node = unicode(xml_or_node, input_encoding)
            root = lxml.etree.fromstring(xml_or_node.strip())

        elif isinstance(xml_or_node, lxml.etree._Element):
            root = xml_or_node

        else:
            raise TypeError(
                u'Unsupported type {}'.format(xml_or_node.__class__))

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
                pretty_print=True)
        else:
            return lxml.etree.tostring(
                return_node.getroottree(),
                encoding=output_encoding,
                xml_declaration=True,
                pretty_print=True)