.. _demo-installation:

Installation & XML Director demo
================================

You have multiple options for trying out XML Director and its features yourself.

Hosted XML Director demo
------------------------

A demo server is provided for you under the URL http://demo.xml-director.info .
You can login into the demo site with username ``demo`` and password ``demo``.
The demo site currently provides some basic demos:

- a folder with all Shakespeare works stored as XML. Each work of Shakespeare
  will be displayed as HTML using the build-in XSLT renderer. In addition a 
  simple PDF version of the work can be generated and downloaded on-the-fly.
  The PDF generation is driven by the Produce & Publish server providing HTML/XML
  conversion to PDF through a "CSS Paged Media" converter (PDFreactor or PrinceXML
  in this case).
- a folder containing a shortened version of an english bible stored as XML.
  The default of of the bible displays the bible grouped by chapters and verses
  natively within the browser without XSLT transformation. The styling is done
  using CSS. The PDF conversion is based on XML and CSS.

Running the XML Director demo yourself using Docker
---------------------------------------------------
The functionality of hosted the XML Director demo is also available as Docker image
that you can run yourself on your own host. The following command can be used
to run the image and access the XML Director installation with your browser on the URL
http://your-host:12020/xml-director::

  docker run -p 12020:12020 zopyx/xmldirector-plone

Building and running XML Director yourself from scratch
-------------------------------------------------------

eXist-db installation
+++++++++++++++++++++

XML Director has been tested with eXist-db 2.2 or higher.
You can download eXist-db yourself directly from www.existdb.org
and install it yourself. You need to remember the configured port and 
username + password specified during the installation process.

Another option is to use Docker (www.docker.org) for running eXist-db
through a pre-configured Docker container image::

    docker run -p 6080:8080 zopyx/existdb-2.2

This will download and run eXist-db version 2.2 and expose its service
on port 6080 (8080 is the port used internally by eXist-db).


Plone installation
++++++++++++++++++


You can build XML Director (which is based on the CMS Plone) on any Linux system
(or MacOS)::

    git clone https://github.com/xml-director/xmldirector.plonecore.git
    cd xmldirector.plonecore
    make build-demo
    # or 'make build' if you want only the standard installation without demo data.
    bin/instance fg

- Login into the site http://your-host:12020/manage using username ``admin`` and password ``admin``
- click on ``Add Plone Site`` and choose the "XML Director demo" profile
- after some seconds you will be redirected to the installed Plone site running XML Director

Verify the ``XML Director settings`` within the Plone ``Site setup``. The webdav URL for eXist-db
must be like::

    http://localhost:6080/exist/webdav/db

where ``6080`` is the port of your eXist-db installation (or ``8080`` for the default installation
with demo data (``make build-demo``).

