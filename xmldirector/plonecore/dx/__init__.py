# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


# Workaround for bad Plone 5 behavior :
# https://github.com/plone/Products.CMFPlone/issues/1533

try:
    from plone.app.dexterity.browser.types import ALLOWED_FIELDS
    ALLOWED_FIELDS.append('.xml_field.XML')
    ALLOWED_FIELDS.append('.xml_image.XML')
    ALLOWED_FIELDS.append('.xml_binary.XML')

except:
    pass
