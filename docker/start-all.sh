#!/bin/bash 
export IGNORE_FS_ENCODING=1
export LC_ALL="en_US.UTF-8"
export LANG="en_US.UTF-8"

git pull
bin/develop update --force
bin/buildout -c demo.cfg 
echo starting existdb
nohup /home/plone/exist/tools/wrapper/bin/exist.sh console &
sleep 60 
cd /home/plone/xmldirector.plonecore
echo setting up plone
bin/instance run src/xmldirector.demo/democontent/setup-plone.py docker
echo starting plone
bin/instance fg
