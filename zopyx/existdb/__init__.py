################################################################
# zopyx.existdb
# (C) 2013,  ZOPYX Limited, D-72074 Tuebingen, Germany
################################################################

try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)

from zope.i18nmessageid import MessageFactory

MessageFactory = MessageFactory('eteaching.policy')
