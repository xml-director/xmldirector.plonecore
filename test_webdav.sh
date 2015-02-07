# Test xmldirector.plonecore against all supported database backend
# The specified webdav endpoint are based on Docker containers:
#
# docker run zopyx/existdb-2.2
# docker run zopyx/basex-80

export WEBDAV_USERNAME=user
export WEBDAV_PASSWORD=user

export WEBDAV_URL=http://demo.xml-director.info:7000
echo '######################################################'
echo Tests against EXISTDB
echo $WEBDAV_URL
echo '######################################################'
bin/test xmldirector.plonecore -D 

