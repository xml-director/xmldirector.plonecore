################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import os
import lxml.etree


XSLT_REGISTRY = {}

# The XSLT registries stores pre-compiled XSLT transformations as a dictionary
# where the keys are composed of a tuple (family, stylesheet_name).  ``family``
# could be used to represent a project, a customer etc.  and
# ``stylesheet_name`` would represent the name of the XSLT transformation.
# Both ``family`` and ``stylesheet_name`` are completey arbitrary.


def register_stylesheet(family, stylesheet_name, stylesheet_path):
    """ Register a Stylesheet as tuple (family, stylesheet_name) """

    key = '{}::{}'.format(family, stylesheet_name)
    if key in XSLT_REGISTRY:
        raise ValueError(
            'Stylesheet {}/{} already registered'.format(family, stylesheet_name))

    if not os.path.exists(stylesheet_path):
        raise ValueError(
            'Stylesheet {}/{} not found ({})'.format(family, stylesheet_name, stylesheet_path))

    with open(stylesheet_path, 'rb') as fp:
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

        XSLT_REGISTRY[key] = transform


def get_stylesheet(family, stylesheet_name):
    """ Return a pre-compiled XSLT transformation by (family, stylesheet_name) """

    key = '{}::{}'.format(family, stylesheet_name)
    if key not in XSLT_REGISTRY:
        raise ValueError(
            'Stylesheet {}/{} not registered'.format(family, stylesheet_name))
    return XSLT_REGISTRY[key]
