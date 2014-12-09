# -*- coding: utf-8 -*-

################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import lxml.etree
import zope.interface
from plone.indexer import indexer
from Products.CMFCore.utils import getToolByName

from zopyx.existdb.dx.xpath_field import get_all_fields
from zopyx.existdb.dx.xml_field import XMLFieldDataManager
from zopyx.existdb.dx.xml_field import XMLText


@indexer(zope.interface.Interface)
def SearchableText(obj):
    """ Index XML """

    try:
        obj.__xml_storage_id__
    except AttributeError:
        return

    fields = get_all_fields(obj)

    # Throw all XML content of all fields into the huge SearchableText bag
    for xml_field in [field for field in get_all_fields(obj).values() if isinstance(field, XMLText)]:
        adapter = XMLFieldDataManager(context=obj, field=xml_field)
        xml = adapter.get()
        if xml:
            root = lxml.etree.fromstring(xml)
            result = []
            for node in root.iter():
                text = node.text.strip()
                if text:
                    result.append(text)
            return unicode(' '.join(result), 'utf-8')
