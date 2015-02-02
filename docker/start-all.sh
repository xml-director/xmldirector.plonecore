#!/bin/bash 
git pull
bin/develop update --force
echo starting existdb
/home/plone/exist/tools/wrapper/bin/exist.sh start 
netstat -nap
cd /home/plone/xmldirector.plonecore
echo setting up plone
bin/instance run src/xmldirector.demo/democontent/setup-plone.py docker
echo starting plone
bin/instance fg
