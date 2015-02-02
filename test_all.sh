# Test xmldirector.plonecore against all supported database backend
# The specified webdav endpoint are based on Docker containers:
#
# docker run zopyx/existdb-2.2
# docker run zopyx/basex-80

export WEBDAV_USERNAME=admin
export WEBDAV_PASSWORD=admin

export WEBDAV_URL=http://demo.xml-director.info:22081/exist/webdav/db
echo '######################################################'
echo Tests against EXISTDB
echo $WEBDAV_URL
echo '######################################################'
bin/test xmldirector.plonecore

export WEBDAV_URL=http://demo.xml-director.info:22080/webdav
echo '######################################################'
echo Tests against BASEX
echo $WEBDAV_URL
echo '######################################################'
bin/test xmldirector.plone
