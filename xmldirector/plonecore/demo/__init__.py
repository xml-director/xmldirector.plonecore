# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
from xmldirector.plonecore.xslt_registry import XSLTRegistryUtility

import xmldocument  # NOQA

cwd = os.path.dirname(__file__)
XSLTRegistryUtility.register_stylesheet(
    'demo', 'play.xsl', os.path.join(cwd, 'play.xsl'))
