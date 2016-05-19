import datetime
from AccessControl.SecurityManagement import newSecurityManager
from zope.component.hooks import setSite
import time

path = sys.argv[-1]

acl_users = app.acl_users
user = acl_users.getUser('admin')
newSecurityManager(None, user.__of__(acl_users))

connector = app.restrictedTraverse(path)
site = connector.aq_parent
print connector
setSite(site)
print site

while 1:
    print 'scanning'
    handle = connector.get_handle()
    result = handle.listdirinfo()
    now = datetime.datetime.utcnow()
    for path, info in result:
        age = now - info['modified_time']
        if age.seconds < 60:
            print 'new', path.encode('utf8'), now - info['modified_time']

    time.sleep(5)
