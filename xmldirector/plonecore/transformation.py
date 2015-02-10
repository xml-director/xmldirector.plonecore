################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import inspect
import time
import lxml.etree
import lxml.html


from zope.component import getUtility
from xmldirector.plonecore.interfaces import ITransformerRegistry
from xmldirector.plonecore.logger import LOG


class Transformer(object):

    def __init__(self, steps=[], context=None, destdir=None, **params):
        self.steps = steps
        self.context = context
        self.destdir = destdir
        self.params = params

    def verify_steps(self):
        """ Verify all transformation steps """

        registry = getUtility(ITransformerRegistry)
        errors = list()
        for family, name in self.steps:
            try:
                registry.get_transformation(family, name)
            except ValueError:
                errors.append(step)
        if errors:
            raise ValueError('Unknown transformer steps: {}'.format(errors)


    def __call__(self, xml_or_node, input_encoding=None, output_encoding=unicode)

        self.verify_steps()

        if isinstance(xml_or_node, basestring):
            if not isinstance(xml_or_node, unicode):
                if not input_encoding:
                    raise TypeError('Input data must be unicode')
                xml = unicode(html, input_encoding)
                xml = xml.strip()
                root = lxml.html.fromstring(html)

        elif instance(xml_or_node, lxml.etree.Element):
            pass

        else:
            raise TypeError(u'Unsupported type {}'.format(xml_or_node.__class__)

        for family, name in self.steps:

            transformer = registry.get_transformation(family, name)
            params = dict(context=self.context,
                          request=getattr(self.context, 'REQUEST', None),
                          destdir=self.destdir,
                          )
            params.update(self.params)
            transformer(root, params)
            LOG.info('Transformation %-30s: %3.6f seconds' % (name, time.time()-ts))

        if output_encoding == unicode:
            return lxml.etree.tostring(
                    root, 
                    encoding=unicode, 
                    pretty_print=True)
        else:
            return lxml.etree.tostring(
                    root.getroottree(), 
                    encoding=output_encoding,
                    xml_declaration=True,
                    pretty_print=True)

