# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


from plone.app.layout.viewlets import ViewletBase
from xmldirector.plonecore.dx import util


class Debug(ViewletBase):

    def info(self):
        if not util.is_xml_content(self.context):
            return
        return dict(storage_key=util.get_storage_key(self.context),
                    storage_path=util.get_storage_path(self.context))
