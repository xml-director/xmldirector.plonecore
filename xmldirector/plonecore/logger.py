# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import logging
import datetime
import pprint

import plone.api
import zope.interface
from DateTime import DateTime
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations
from BTrees.OOBTree import OOBTree

LOG = logging.getLogger('xmldirector.plonecore')

requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)
urllib3_log = logging.getLogger("urllib3")
urllib3_log.setLevel(logging.WARNING)


LOG_KEY = 'xmldirector.plonecore.connector.log'


class IPersistentLogger(zope.interface.Interface):

    """ Marker interface for a object persistent logger """


class PersistentLoggerAdapter(object):

    """ An adapter for storing logging information as an annotation
        on a persistent object.
    """

    zope.interface.implements(IPersistentLogger)

    def __init__(self, context):
        self.context = context

    @property
    def entries(self, min_datetime=None, max_datetime=None):
        return self.annotations.values(min_datetime, max_datetime)

    def __len__(self):
        return len(self.entries)

    @property
    def annotations(self):
        all_annotations = IAnnotations(self.context)
        if LOG_KEY not in all_annotations:
            all_annotations[LOG_KEY] = OOBTree()
        else:
            annotations = all_annotations[LOG_KEY]
            if isinstance(annotations, PersistentList):
                tree = OOBTree()
                for d in annotations:
                    tree[d['date']] = d
                all_annotations[LOG_KEY] = tree
        return all_annotations[LOG_KEY]

    def log(self, comment, level='info', details=None):
        """ Add a log entry """
        annotations = self.annotations
        if details:
            if not isinstance(details, basestring):
                details = pprint.pformat(details)
        d = dict(date=datetime.datetime.utcnow(),
                 username=plone.api.user.get_current().getUserName(),
                 level=level,
                 details=details,
                 comment=comment)
        annotations[d['date']] = d
        annotations._p_changed = 1
        self.context.setModificationDate(DateTime())

    def clear(self):
        """ Clear all logger entries """
        annotations = IAnnotations(self.context)
        annotations[LOG_KEY] = OOBTree()
