XML Director demo
=================

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
The functionality of hosted XML Director demo is also available as Docker image
that you can run yourself on your own host. The following command can be used
to run the image and access the XML Director installation with your browser on the URL
http://your-host:12020/xml-director::

  docker run -p 12020:12020 zopyx/xmldirector-plone

Building and running XML Director yourself from scratch
-------------------------------------------------------

You can build XML Director (which is based on the CMS Plone) on any Linux system
(or MacOS)::

    git clone https://github.com/xml-director/xmldirector.plonecore.git
    cd xmldirector.plonecore
    make build-demo
    bin/instance fg

- Login into the site http://your-host:12020/manage using username ``admin`` and password ``admin``
- click on ``Add Plone Site`` and choose the "XML Director demo" profile
- after some seconds you will be redirected to the installed Plone site running XML Director

