#!/bin/bash 
git pull
bin/develop update --force
bin/buildout -c demo.cfg 
echo starting existdb
nohup /home/plone/exist/tools/wrapper/bin/exist.sh console &
sleep 60 
netstat -nap
cd /home/plone/xmldirector.plonecore
echo setting up plone
bin/instance run src/xmldirector.demo/democontent/setup-plone.py docker
echo starting plone
netstat -nap
bin/instance fg
