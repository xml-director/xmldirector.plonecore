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

#virtualenv-2.7 .
pip install -U setuptools==7.0  
pip install boto
python bootstrap.py -c $config --setuptools-version 20.2.2 --version 2.5
bin/buildout -c $config

if [[ $TYPE  == 'OWNCLOUD' ]]
then
    wget http://localhost:8080
fi

bin/test -s xmldirector.plonecore

