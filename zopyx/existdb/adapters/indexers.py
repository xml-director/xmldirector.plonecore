
from plone.indexer import indexer
from zopyx.existdb.connector import IConnector

@indexer(IConnector)
def SearchableText(obj):
    """ Index HTML """

    from zopyx.existdb.browser.connector import Connector as CView

    view = CView(obj, obj.REQUEST)
    return view.searchabletext()

