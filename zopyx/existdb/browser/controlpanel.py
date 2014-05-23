# -*- coding: utf-8 -*-

from plone.app.registry.browser import controlpanel

from zopyx.existdb.interfaces import IExistDBSettings
from zopyx.existdb import MessageFactory as _


class ExistDBSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IExistDBSettings
    label = _(u'eteaching.policy settings')
    description = _(u'')

    def updateFields(self):
        super(ExistDBSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(ExistDBSettingsEditForm, self).updateWidgets()


class ExistDBSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ExistDBSettingsEditForm
