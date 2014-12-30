# Test xmldirector.plonecore against all supported database backend
# The specified webdav endpoint are based on Docker containers

export WEBDAV_USERNAME=admin
export WEBDAV_PASSWORD=admin

export WEBDAV_URL=http://dev1.veit-schiele.de:22081/exist/webdav/db
echo '######################################################'
echo Tests against EXISTDB
echo $WEBDAV_URL
echo '######################################################'
bin/test xmldirector

export WEBDAV_URL=http://dev1.veit-schiele.de:22080/webdav
echo '######################################################'
echo Tests against BASEX
echo $WEBDAV_URL
echo '######################################################'
bin/test xmldirector
