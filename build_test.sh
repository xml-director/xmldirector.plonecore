#!/bin/bash

export PATH=\
/opt/buildout.python/bin:\
$PATH:

echo $WEBDAV_URL
echo $PLONE_VERSION
echo $DOCKER

config=buildout-plone-$PLONE_VERSION.cfg

docker pull $DOCKER
docker run -d -p 127.0.0.1:8080:8080 $DOCKER

#virtualenv-2.7 .
pip install -U setuptools==7.0  
python bootstrap.py -c $config --setuptools-version 18.4 --version 2.2.5
bin/buildout -c $config
bin/test -s xmldirector.plonecore
##bin/coverage run bin/test
