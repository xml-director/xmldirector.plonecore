xmldirector.plonecore
=====================

.. note:: This module  

  - *is* a solution for mounting XML databases like eXist-db or
    BaseX into Plone through their WebDAV port
  - *is* a solution for construction Dexterity content-types programmatically
    or through-the-web with XML related fields where the content is stored
    in BaseX or eXist-db
  - *is* an _experimental_ solution for mounting general WebDAV 
    services into Plone
  - *is not* a replacement for the ZODB 

``xmldirector.plonecore`` is the technical foundation of the XML-Director
project (www.xml-director.info). The goal of the XML-Director project is
building an enterprise-level XML content management system on top of the CMS
Plone (www.plone.org) with support for XML databases like eXis-db or Base-X.
However the underlaying implementation can also be used to mount arbitrary
backend through WebDAV into Plone.


``xmldirector.plonecore`` integrates  Plone 4.3 (later Plone 5.0) with 
eXist-db or Base-X or providing the following features:

- mounts an arbitary eXist-db or Base-X collection into Plone
- ACE editor integration
- ZIP export from eXist-db or Base-X
- ZIP import into eXist-db or Base-X
- pluggable view mechanism for configuring custom views for XML database  
  content by filename and view name
- create, rename or delete collections through the web
- extensible architecture through Plone Dexterity behaviors
- support for XQuery scripts called through the RESTXQ layer of eXist-db
  (allows you to call XQuery scripts and return the output format (JSON,
  HTML, XML) depending on your application requirements)
- dedicated per-connector logging facility
- small and extensible
- experimental support for mounting arbitrary WebDAV service into Plone 

  - ``XMLText`` - a field for storing XML content in BaseX or eXist-db

  - ``XPathField`` - for retrieving parts of XML content stored within a 
    ``XMLText`` field through an XPath expression (e.g. for extracting
    and displaying metadata from XML content)

  - ``XMLBinary`` and ``XMLImage`` fields for storing binary data and images
    in BaseX or eXist-db. The functionality is identical with the standard
    Dexterity file and image fields (except for the different storage layer)
 

The primary usecase for ``xmldirector.plonecore`` is the integration of XML document
collections into Plone using eXist-db or Base-X as storage layer. ``xmldirector.plonecore`` is
not storage layer for Plone content in the first place although it could be
used in some way for storing primary Plone content (or parts of the content)
inside eXist-db or Base-X. There is no build-in support for mapping metadata as stored in
XML documents to Plone metadata or vice versa. However this could be
implemented easily in application specific code build on top of
``xmldirector.plonecore``. The design goal of ``xmldirector.plonecore`` is to provide the basic
functionality for integrating Plone with eXist-db or Base-X without implementing any
further specific application requirements.  Additional functionality can be
added through Dexterity behaviors, supplementary browser views, event lifecycle
subscribers and related technology.


Requirements
------------

- Plone 4.3 (tested)
  
- Plone 5.0 (experimental, in progress)

- Supported XML backends:

    - eXist-db 2.2 or higher

    - or Base-X 8.2 or higher

- (un)supported/experimental WebDAV backends:

    - OwnCloud
    
    - Alfresco


Configuration
-------------

Goto the Plone control panel and click on the ``XML-Director Core`` configlet and
configure the 

- WebDAV URL of the XML database. 

  For eXist-db you need something like::
  
    http://localhost:6080/existdb/webdav/db

  For Base-X 8 you need::

    http://localhost:8984/webdav
  

- WebDAV username

- WebDAV password


Using xmldirector.plonecore
---------------------------

The package provides a new content-types ``Connector`` that will include
eXist-db or Base-X into Plone - either from the top-level collection of your eXist-db/Base-X
database or from a subcollection. You can browse and traverse into
subcollections, view single documents or edit text-ish content through the web
(using the build-in ACE editor integration).

All connection settings (URL, username and password can be overriden on 
the connector level) in order to ignore the Plone site-wide eXist-db
settings).

.. note:: This module provides a generic integration of arbitrary 
   WebDAV services like OwnCloud, BaseX (over WebDAV) or even other Plone
   serves (exposed through the Plone WebDAV source port) with Plone.
   This integration is highly experimental and not the primary purpose
   of ``xmldirector.plonecore``. Use the functionality at your own risk.
   In order to use this module together with WebDAV services other than the
   XML database eXist-db: you have to set the emulation mode to ``webdav``
   inside the eXist-db control panel of Plone

Dexterity fields
----------------

``xmldirector.plonecore`` comes with the following Dexterity fields that
can be either used programmatically in your own field schema or through-the-web.

XMLText
+++++++
The ``XMLText`` can be used to store *valid* XML content. The field is rendered
without Plone using the ACE editor. You can perform a client-side XML validation
within the edit mode of a document by clicking on the ``Validate XML`` button.
A document with invalid XML content can not be submitted or saved. Invalid XML
will be rejected with an error message through the edit form.

XMLXPath
++++++++

The ``XMLXPath`` field can be used to reference an ``XMLText`` field in order
to display a part of the XML content using an XPath expression.

Example

An ``XMLPath`` field with field name ``myxml`` might contain the following XML
content::

    <?xml version="1.0"?>
    <doc>
        <metadata>
            <title>This is a text</title>
        </metdata>
        <body>....</body>
    </doc>

In order to extract and display the <title> text within a dedicated Dexterity field
you can use the following extended expression:

    field=<fieldname>,xpath=<xpath expression>

In this case you would use:

    field=myxml,xpath=/doc/metadata/title/text()

Note that the current syntax is very rigid and does not allow any whitespace
characters expect within the <xpath expression>.


XMLBinary, XMLImage
+++++++++++++++++++
Same as file and image field in Plone but with BaseX or eXist-db as
storage layer.


License
-------
This package is published under the GNU Public License V2 (GPL 2)

Source code
-----------
See https://bitbucket.org/onkopedia/xmldirector.plonecore

Bugtracker
----------
See https://bitbucket.org/onkopedia/xmldirector.plonecore

Travis-CI
---------

See https://travis-ci.org/xml-director/xmldirector.plonecore

.. image:: https://travis-ci.org/xml-director/xmldirector.plonecore.svg?branch=master
    :target: https://travis-ci.org/xml-director/xmldirector.plonecore

Credits
-------
The development of ``xmldirector.plonecore`` was funded as part of a customer project
by Deutsche Gesellschaft für Hämatologie und medizinische Onkologie (DGHO).


Author
------
| Andreas Jung/ZOPYX
| Hundskapfklinge 33
| D-72074 Tuebingen, Germany
| info@zopyx.com
| www.zopyx.com

