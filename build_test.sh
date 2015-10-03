#!/bin/bash

export PATH=\
/opt/buildout.python/bin:\
$PATH:

echo $WEBDAV_URL
echo $PLONE_VERSION

config=buildout-plone-$PLONE_VERSION.cfg

export WEBDAV_URL=http://demo.xml-director.info:22081/exist/webdav/db

virtualenv-2.7 .
bin/pip install -U setuptools==18.2  
bin/python bootstrap.py -c $config --setuptools-version 18.2 --version 2.2.5

bin/buildout -c $config
bin/test -s xmldirector.plonecore
##bin/coverage run bin/test
