################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
from xmldirector.plonecore import xslt_registry

import xmldocument  # NOQA

cwd = os.path.dirname(__file__)
xslt_registry.register_stylesheet(
    'demo', 'play.xsl', os.path.join(cwd, 'play.xsl'))
