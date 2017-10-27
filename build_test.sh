#!/bin/bash

set -x

export PATH=\
/opt/buildout.python/bin:\
$PATH:

echo $CONNECTOR_URL
echo $PLONE_VERSION
echo $DOCKER
echo $DOCKER_OPTIONS

config=buildout-plone-$PLONE_VERSION.cfg

docker run -d $DOCKER_OPTIONS $DOCKER
docker run -d $DOCKER_OPTIONS $DOCKER

virtualenv .
bin/pip install zc.buildout
ln -sf base.cfg buildout.cfg
bin/buildout bootstrap
bin/buildout -c $config

if [[ $TYPE  == 'OWNCLOUD' ]]
then
    wget http://localhost:8080
fi

bin/test -s xmldirector.plonecore

