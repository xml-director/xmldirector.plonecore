# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


# Workaround for bad Plone 5 behavior :
# https://github.com/plone/Products.CMFPlone/issues/1533

try:
    from plone.app.dexterity.browser.types import ALLOWED_FIELDS
    ALLOWED_FIELDS.append('xmldirector.plonecore.dx.xmltext_field.XML')
    ALLOWED_FIELDS.append('xmldirector.plonecore.dx.xmlimage_field.XML')
    ALLOWED_FIELDS.append('xmldirector.plonecore.dx.xmlbinary_field.XML')
    ALLOWED_FIELDS.append('xmldirector.plonecore.dx.xmlxpath_field.XML')
except:
    pass
