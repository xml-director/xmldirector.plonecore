# Test xmldirector.plonecore against all supported database backend
# The specified webdav endpoint are based on Docker containers:
#
# docker run zopyx/existdb-2.2
# docker run zopyx/basex-80

export CONNECTOR_USERNAME=admin
export CONNECTOR_PASSWORD=admin

export CONNECTOR_URL=http://demo.xml-director.info:22082/exist/webdav/db
echo '######################################################'
echo Tests against EXISTDB 3.0
echo $CONNECTOR_URL
echo '######################################################'
bin/test xmldirector.plonecore
bin/test-crex xmldirector.crex


export CONNECTOR_URL=http://demo.xml-director.info:22081/exist/webdav/db
echo '######################################################'
echo Tests against EXISTDB 2.2
echo $CONNECTOR_URL
echo '######################################################'
bin/test xmldirector.plonecore
bin/test-crex xmldirector.crex

export CONNECTOR_URL=http://demo.xml-director.info:22080/webdav
echo '######################################################'
echo Tests against BASEX  8.3
echo $CONNECTOR_URL
echo '######################################################'
bin/test xmldirector.plone
bin/test-crex xmldirector.crex

mkdir /tmp/testing
rm -fr /tmp/testing/*
export CONNECTOR_URL=file:///tmp/testing
echo '######################################################'
echo Tests against LOCALFS
echo $CONNECTOR_URL
echo '######################################################'
bin/test xmldirector.plone
bin/test-crex xmldirector.crex
