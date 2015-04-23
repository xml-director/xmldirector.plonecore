# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import defusedxml.lxml
import zope.interface
from plone.indexer import indexer

from xmldirector.plonecore.dx import util
from xmldirector.plonecore.dx.xpath_field import get_all_fields
from xmldirector.plonecore.dx.xml_field import XMLFieldDataManager
from xmldirector.plonecore.dx.xml_field import XMLText

from xmldirector.plonecore.logger import LOG


@indexer(zope.interface.Interface)
def SearchableText(obj):
    """ Wrapper code for catching and logging error inside the indexer
        because plone.indexer is stupid and swallows errors without logging.
    """

    try:
        return _SearchableText(obj)
    except Exception as e:
        LOG.error('SearchableText indexer error ({})'.format(e), exc_info=True)
        raise


def _SearchableText(obj):
    """ Index XML """

    if not util.is_xml_content(obj):
        return

    # Throw all XML content of all fields into the huge SearchableText bag
    result = []
    for xml_field in [field for field in get_all_fields(obj).values() if isinstance(field, XMLText)]:
        adapter = XMLFieldDataManager(context=obj, field=xml_field)
        xml = adapter.get()
        if xml:
            root = defusedxml.lxml.fromstring(xml)
            for node in root.iter():
                if node.text:
                    text = node.text.strip()
                    if text:
                        if not isinstance(text, unicode):
                            text = unicode(text, 'utf8')
                        result.append(text)

    if result:
        return u' '.join(result)
