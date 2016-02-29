################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import furl
from fs.opener import Opener


class DropboxOpener(Opener):
    names = ['dropbox']
    desc = """Opens a Dropbox """

    @classmethod
    def get_fs(cls, registry, fs_name, fs_name_params, fs_path, writeable, create_dir):
        from xmldirector.plonecore.drivers import dropboxfs

        url = fs_path
        if '://' not in url:
            url = 'dropbox://' + url

        f = furl.furl(url)
        username = str(f.username)
        password = str(f.password)
        if '+' not in username:
            raise ValueError('username must be \'<app_key>+<app_secret>\'')
        app_key, app_secret = username.split('+')
        if '+' not in password:
            raise ValueError(
                'password must be \'<access_token>+<access_token_secret>\'')
        access_token, access_token_secret = password.split('+')
        fs = dropboxfs.DropboxFS(
            app_key, app_secret, 'dropbox', access_token, access_token_secret)
        return fs, ''


from fs.opener import opener
opener.add(DropboxOpener)
