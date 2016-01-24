FROM fedora:22
MAINTAINER Andreas Jung <info@zopyx.com>
RUN dnf -y update
RUN dnf -y install python-virtualenv gcc-c++ libxml2-devel libxslt-devel libjpeg-devel zlib-devel git-core wv java-1.8.0-openjdk expect gettext net-tools procps-ng patch 

RUN useradd -u 5555 -ms /bin/bash plone

USER 5555 
WORKDIR /home/plone

RUN curl -LO http://downloads.sourceforge.net/exist/Stable/2.2/eXist-db-setup-2.2.jar
ADD exist-setup.cmd /home/plone/exist-setup.cmd
RUN expect -f exist-setup.cmd
RUN rm eXist-db-setup-2.2.jar exist-setup.cmd
ENV EXIST_HOME /home/plone/exist


RUN virtualenv .
RUN bin/pip install grampg
RUN git clone https://github.com/xml-director/xmldirector.plonecore.git  
WORKDIR xmldirector.plonecore
RUN git pull
RUN ../bin/python bootstrap.py --setuptools-version=7.0 --version=2.2.5 -c buildout-plone-4.3.cfg

RUN bin/buildout -c demo.cfg

EXPOSE 8080 8443 12020
