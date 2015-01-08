# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

import mimetypes
import lxml.html

from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZPublisher.Iterators import IStreamIterator

from .view_registry import precondition_registry
from .view_registry import Precondition
from . import config


class webdav_iterator(file):

    implements(IStreamIterator)

    def __init__(self, handle, mode='rb', streamsize=1 << 16):
        self.fp = handle.open('.', mode)
        self.streamsize = streamsize

    def next(self):
        data = self.fp.read(self.streamsize)
        if not data:
            raise StopIteration
        return data

    def __len__(self):
        cur_pos = self.fp.tell()
        self.fp.seek(0, 2)
        size = self.fp.tell()
        self.seek(cur_pos, 0)
        return size


# Default view  for connector

def default_html_handler(webdav_handle, filename, view_name, request):

    html_template = ViewPageTemplateFile('html_view.pt')

    # exist-db base url
    base_url = '{}/view/{}'.format(request.context.absolute_url(1),
                                   '/'.join(request.subpath[:-1]))

    # get HTML
    html = webdav_handle.open('.', 'rb').read()
    root = lxml.html.fromstring(html)

    # rewrite relative image urls
    for img in root.xpath('//img'):
        src = img.attrib['src']
        if not src.startswith('http'):
            img.attrib['src'] = '{}/{}'.format(base_url, src)

    # rewrite relative image urls
    for link in root.xpath('//link'):
        src = link.attrib['href']
        if not src.startswith('http'):
            link.attrib['href'] = '{}/{}'.format(base_url, src)

    html = lxml.html.tostring(root)
    return html_template.pt_render(dict(
        template='html_view',
        request=request,
        context=request.context,
        options=dict(
            base_url=base_url,
            html=html)))


def ace_editor(webdav_handle, filename, view_name, request,
               readonly=False, template_name='ace_editor.pt'):
    """ Default handler for showing/editing textish content through the ACE editor """

    mt, encoding = mimetypes.guess_type(filename)
    content = webdav_handle.open('.', 'rb').read()
    ace_mode = config.ACE_MODES.get(mt, 'text')
    template = ViewPageTemplateFile(template_name)
    action_url = '{}/view-editor/{}'.format(request.context.absolute_url(),
                                            '/'.join(request.subpath))
    return template.pt_render(dict(
        template='ace_editor.pt',
        request=request,
        context=request.context,
        options=dict(content=content,
                     action_url=action_url,
                     readonly=readonly,
                     ace_readonly=str(readonly).lower(),  # JS
                     ace_mode=ace_mode)))


def ace_editor_readonly(webdav_handle, filename, view_name,
                        request, readonly=True, template_name='ace_editor.pt'):
    return ace_editor(
        webdav_handle, filename, view_name, request, readonly, template_name)


def default_view_handler(webdav_handle, filename, view_name, request):
    """ Default handler for images and other binary resources """

    info = webdav_handle.getinfo('.')
    mt, encoding = mimetypes.guess_type(filename)
    if not mt:
        mt = 'application/octet-stream'
    request.response.setHeader('Content-Type', mt)
    if 'filename' in request:
        request.response.setHeader(
            'Content-Disposition', 'attachment;filename={}'.format(request['filename']))
    if 'size' in info:
        request.response.setHeader('Content-Length', info['size'])
        return webdav_iterator(webdav_handle)
    else:
        data = webdav_handle.open('.', 'rb').read()
        request.response.setHeader('Content-Length', len(data))
        return data


precondition_registry.register(Precondition(suffixes=['.html', '.htm'],
                                            view_names=['view'],
                                            view_handler=default_html_handler))
precondition_registry.register(Precondition(suffixes=['.xml', '.html', '.htm', '.css', '.json'],
                                            view_names=['view-editor'],
                                            view_handler=ace_editor))
precondition_registry.register(Precondition(suffixes=['.xml', '.html', '.htm', '.css', '.json'],
                                            view_names=[
                                                'view-editor-readonly'],
                                            view_handler=ace_editor_readonly))
precondition_registry.set_default(
    Precondition(view_handler=default_view_handler))
