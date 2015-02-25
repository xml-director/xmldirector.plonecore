################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################



from Products.Five.browser import BrowserView
from xmldirector.plonecore.browser.api import API


class LockManager(BrowserView):

    def entries(self):
        api_view = API(context=None, request=self.request)
        results = api_view.generic_query('all-locks', deserialize_json=True)
        if results:
            return results['lock']
        return ()
