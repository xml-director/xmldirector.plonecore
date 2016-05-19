# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import json
from plone.rest.service import Service
from ZPublisher.Iterators import IStreamIterator


def Service__call__(self):
    self.request.response.setHeader("Content-Type", "application/json")
    result = self.render()
    if IStreamIterator.providedBy(result):
        return result
    return json.dumps(result, indent=2, sort_keys=True)

Service.__call__ = Service__call__
