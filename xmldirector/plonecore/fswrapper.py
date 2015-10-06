# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


from furl import furl

from xmldirector.plonecore.davfs import have_boto
from xmldirector.plonecore.davfs import have_paramiko
from xmldirector.plonecore.davfs import DAVFSWrapper
from xmldirector.plonecore.davfs import OSFSWrapper
from xmldirector.plonecore.davfs import FTPFSWrapper


def get_fs_wrapper(url, credentials=None):

    if not url.endswith('/'):
        url += '/'
    f = furl(url)
    original_url = url
    if f.scheme == 'file':
        wrapper = OSFSWrapper(url[7:], encoding='utf-8')
    elif f.scheme == 'http':
        wrapper = DAVFSWrapper(original_url, credentials)
    elif f.scheme == 'https':
        wrapper = DAVFSWrapper(original_url, credentials)
    elif f.scheme == 's3':
        if have_boto:
            from xmldirector.plonecore.davfs import S3FSWrapper
            wrapper = S3FSWrapper(
                    bucket=f.host, 
                    prefix=str(f.path),
                    aws_access_key=credentials['username'],
                    aws_secret_key=credentials['password'])
        else:
            raise ValueError('boto module is not installed')
    elif f.scheme == 'sftp':

        if have_paramiko:
            from xmldirector.plonecore.davfs import SFTPFSWrapper
            wrapper = SFTPFSWrapper(connection=f.host,
                                    root_path=str(f.path),
                                    username=f.username,
                                    password=f.password)
        else:
            raise ValueError('paramiko module is not installed')

    elif f.scheme == 'ftp':
        wrapper = FTPFSWrapper(host=f.host,
                               user=f.username,
                               passwd=f.password)
    else:
        raise ValueError('Unsupported URL schema {}'.format(original_url))

    wrapper.url = url
    return wrapper
