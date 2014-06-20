# -*- coding: utf-8 -*-

################################################################
# zopyx.existdb
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

from plone.app.registry.browser import controlpanel

from zopyx.existdb.interfaces import IExistDBSettings
from zopyx.existdb.i18n import MessageFactory as _


class ExistDBSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IExistDBSettings
    label = _(u'eXistdb settings')
    description = _(u'')

    def updateFields(self):
        super(ExistDBSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(ExistDBSettingsEditForm, self).updateWidgets()


class ExistDBSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ExistDBSettingsEditForm
