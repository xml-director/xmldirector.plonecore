try:
    from zope.i18nmessageid import MessageFactory
    MessageFactory = MessageFactory('zopyx.existdb')
except ImportError:
    pass
