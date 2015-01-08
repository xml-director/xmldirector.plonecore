#!/bin/bash 
echo starting existdb
/home/plone/exist/tools/wrapper/bin/exist.sh start 
netstat -nap
cd /home/plone/xmldirector.plonecore
echo setting up plone
bin/instance run democontent/setup-plone.py
echo starting plone
bin/instance fg
