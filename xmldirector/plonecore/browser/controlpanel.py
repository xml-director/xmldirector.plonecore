# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

from plone.app.registry.browser import controlpanel

from xmldirector.plonecore.interfaces import IWebdavSettings
from xmldirector.plonecore.i18n import MessageFactory as _


class DBSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IWebdavSettings
    label = _(u'XML Director core settings')
    description = _(u'')

    def updateFields(self):
        super(DBSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(DBSettingsEditForm, self).updateWidgets()


class DBSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = DBSettingsEditForm
