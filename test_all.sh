# Test xmldirector.plonecore against all supported database backend
# The specified webdav endpoint are based on Docker containers:
#
# docker run zopyx/existdb-2.2
# docker run zopyx/basex-80

export WEBDAV_USERNAME=admin
export WEBDAV_PASSWORD=admin

export WEBDAV_URL=http://demo.xml-director.info:22082/exist/webdav/db
echo '######################################################'
echo Tests against EXISTDB 3.0
echo $WEBDAV_URL
echo '######################################################'
bin/test xmldirector.plonecore

export WEBDAV_URL=http://demo.xml-director.info:22081/exist/webdav/db
echo '######################################################'
echo Tests against EXISTDB 2.2
echo $WEBDAV_URL
echo '######################################################'
bin/test xmldirector.plonecore

export WEBDAV_URL=http://demo.xml-director.info:22080/webdav
echo '######################################################'
echo Tests against BASEX  8.3
echo $WEBDAV_URL
echo '######################################################'
bin/test xmldirector.plone

mkdir /tmp/testing
rm -fr /tmp/testing/*
export WEBDAV_URL=file:///tmp/testing
echo '######################################################'
echo Tests against LOCALFS
echo $WEBDAV_URL
echo '######################################################'
bin/test xmldirector.plone
