#!/bin/bash 
/home/plone/exist/tools/wrapper/bin/exist.sh start 
cd /home/plone/xmldirector.plonecore
bin/instance run democontent/setup-plone.py
bin/instance fg
