#!/bin/bash

export PATH=\
/opt/buildout.python/bin:\
$PATH:

echo $WEBDAV_URL
echo $PLONE_VERSION

config=buildout-plone-$PLONE_VERSION.cfg

#virtualenv-2.7 .
pip install -U setuptools==7.0  
python bootstrap.py -c $config --setuptools-version 7.0 --version 2.2.5
bin/buildout -c $config
bin/test -s xmldirector.plonecore
##bin/coverage run bin/test
