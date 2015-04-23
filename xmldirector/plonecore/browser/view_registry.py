# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import os
import inspect

from Products.Five.browser import BrowserView

_marker = object


class Precondition(object):

    def __init__(self, suffixes=None, view_names=None, view_handler=None):

        if suffixes is None:
            suffixes = []

        if view_names is None:
            view_names = []

        if not isinstance(suffixes, (list, tuple)):
            raise TypeError('"suffixes" must be list or tuple')
        if not isinstance(view_names, (list, tuple)):
            raise TypeError('"view_names" must be list or tuple')

        self.view_names = view_names
        self.view_handler = view_handler
        self.suffixes = []
        for suffix in suffixes:
            if not suffix.startswith('.'):
                suffix = u'.' + suffix
            self.suffixes.append(suffix)

    def can_handle(self, filename, view_name):

        if view_name not in self.view_names:
            return False

        basename, suffix = os.path.splitext(filename)
        if suffix not in self.suffixes:
            return False

        return True

    def handle_view(self, webdav_handle, filename, view_name, request):
        if inspect.isfunction(self.view_handler):
            return self.view_handler(
                webdav_handle, filename, view_name, request)
        elif inspect.isclass(self.view_handler):
            if issubclass(self.view_handler, BrowserView):
                return self.view_handler(webdav_handle, filename, view_name, request)()
            else:
                return self.view_handler()(webdav_handle, filename, view_name, request)
        raise TypeError(
            'Unsupported kind of view_handler {}'.format(self.view_handler))

    def __str__(self):
        return 'Precondition: {}, {}, {}'.format(
            self.suffixes, self.view_names, self.view_handler)


class PreconditionRegistry(object):

    def __init__(self):
        self._p = list()
        self._p_default = None

    def __len__(self):
        return len(self._p)

    def register(self, precondition, position=_marker):
        if not isinstance(precondition, Precondition):
            raise TypeError('"precondition" must be instance of Precondition')
        if position is not _marker:
            self._p.insert(position, precondition)
        else:
            self._p.append(precondition)

    def set_default(self, precondition):
        self._p_default = precondition

    def dispatch(self, webdav_handle, filename, view_name, request):

        for precondition in self._p:
            if precondition.can_handle(filename, view_name):
                return precondition.handle_view(
                    webdav_handle, filename, view_name, request)

        if self._p_default:
            return self._p_default.handle_view(
                webdav_handle, filename, view_name, request)
        raise ValueError('No matching precondition found')


precondition_registry = PreconditionRegistry()
