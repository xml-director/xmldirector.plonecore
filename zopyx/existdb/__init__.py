################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)

try:
    from zope.i18nmessageid import MessageFactory
    MessageFactory = MessageFactory('zopyx.existdb')
except ImportError:
    pass
