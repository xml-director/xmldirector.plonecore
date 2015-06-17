# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import uuid
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
LOG_LAST_USER = 'xmldirector.plonecore.connector.lastuser'
LOG_LAST_DATE = 'xmldirector.plonecore.connector.lastdate'


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

    def entry_by_uuid(self, target_uuid):
        """ Find a logger entry by uuid """
        for entry in self.entries:
            if target_uuid == entry.get('uuid'):
                return entry
        raise ValueError(
            u'No log entry with UUID {} found'.format(target_uuid))

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
                 uuid=str(uuid.uuid1()),
                 comment=comment)
        annotations[d['date']] = d
        annotations._p_changed = 1
        IAnnotations(self.context)[LOG_LAST_USER] = plone.api.user.get_current().getUserName()
        IAnnotations(self.context)[LOG_LAST_DATE] = datetime.datetime.utcnow()
        self.context.setModificationDate(DateTime())

    def get_last_user(self):
        """ Return username of last user """
        return IAnnotations(self.context).get(LOG_LAST_USER)

    def get_last_date(self):
        """ Return datetime of last time used """
        return IAnnotations(self.context).get(LOG_LAST_DATE)

    def clear(self):
        """ Clear all logger entries """
        annotations = IAnnotations(self.context)
        annotations[LOG_KEY] = OOBTree()
