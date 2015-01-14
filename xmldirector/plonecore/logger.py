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
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations

LOG = logging.getLogger('onkopedia.policy')

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
    def logger(self):
        annotations = IAnnotations(self.context)
        if LOG_KEY not in annotations:
            annotations[LOG_KEY] = PersistentList()
        return annotations[LOG_KEY]

    def log(self, comment, level='info', details=None):
        """ Add a log entry """
        logger = self.logger
        if details:
            if not isinstance(details, basestring):
                details = print.pformat(details)
        entry = dict(date=datetime.datetime.utcnow(),
                     username=plone.api.user.get_current().getUserName(),
                     level=level,
                     details=details,
                     comment=comment)
        logger.append(entry)
        logger._p_changed = 1

    def log_clear(self):
        """ Clear all logger entries """
        annotations = IAnnotations(self.context)
        annotations[LOG_KEY] = PersistentList()
