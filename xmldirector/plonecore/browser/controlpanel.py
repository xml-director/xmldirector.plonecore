# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import fs.errors
from zope.component import getUtility
from plone.app.registry.browser import controlpanel

from xmldirector.plonecore.i18n import MessageFactory as _
from xmldirector.plonecore.interfaces import IWebdavSettings
from xmldirector.plonecore.interfaces import IWebdavHandle


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

    def connection_test(self):

        service = getUtility(IWebdavHandle)
        errors = []

        try:
            handle = service.webdav_handle()
        except fs.errors.PermissionDeniedError as e:
            errors.append(u'Permission denied error - improper credentials? ({})'.format(e))
            return errors
        except fs.errors.ResourceNotFoundError as e:
            errors.append(u'Resource not found - local webdav path correct? ({})'.format(e))
            return errors
        except fs.errors.RemoteConnectionError as e:
            errors.append(u'WebDAV URL incorrect! ({})'.format(str(e)))
            return errors

        return errors
