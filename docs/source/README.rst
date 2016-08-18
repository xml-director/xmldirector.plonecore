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


``xmldirector.plonecore`` integrates  Plone 4.3 or 5.1 with 
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
  
- Plone 5.0 (tested)

- Plone 5.1 (unsupported to due the alpha state of Plone 5.1)  

- Supported backends:

    - eXist-db 2.2 and 3.0

    - Base-X >= 8.2

    - OwnCloud
    
    - Alfresco

    - Marklogic Server

    - Dropbox (via dropdav.com (Dropbox to WebDAV bridge, paid SaaS) or via xmldirector.dropbox)

    - AWS S3

    - Cloud federation services

      - Otixo.com
      - Storagemadeeasy.com

- experimental support for the following backends/protocols (don't
  use XML Director with these protocols/backends in production):

    - FTP (working in general, open issues with the connection pool)
    
    - SFTP (working in general, open issues with the connection pool)


Configuration
-------------

Goto the Plone control panel and click on the ``XML-Director Core`` configlet and
configure the your service

ExistDB
+++++++
  
- http://localhost:6080/existdb/webdav/db
- username and password required to access your XML database over WebDAV

BaseX
+++++

- http://localhost:8984/webdav                                     
- username and password required to access your XML database over WebDAV

Owncloud
++++++++

- http://hostname:port/remote.php/webdav
- username and password required to access your Owncloud instance over WebDAV

Alfresco
++++++++

- http://hostname:port/webdav
- username and password required to access your Alfresco instance over WebDAV

Dropbox (via dropdav.com SaaS)
++++++++++++++++++++++++++++++

- https://dav.dropdav.com
- username and password required of your dropdav.com account

Dropbox (via xmldirector.dropbox)
+++++++++++++++++++++++++++++++++

- dropbox://dropbox.com
- access to Dropbox must be authenticated using OAuth 
  (see xmldirector.dropbox documentation)

SME (storagemadeeasy.com)
+++++++++++++++++++++++++

- https://webdaveu.storagemadeeasy.com   (EU)
- https://webdav.storagemadeeasy.com (US)
- username and password required of your storagemadeeasy.com account

Otixo.com
+++++++++

- https://otixo.com
- username and password required of your otixo.com account

Local filesystem
++++++++++++++++

- file:///path/to/some/directory
- no support for credentials, the referenced filesystem must be readable (and writable)

AWS S3
++++++
    
- s3://bucketname
- enter your AWS access key as username and the AWS secret key as password
- you need to install the ``boto`` module (either using ``pip`` or using zc.buildout)

FTP
+++

- ftp://hostname/path/to/directory
- username and password that are necessary to access the configured directory path
  through FTP

SFTP
++++

- sftp://hostname/path/to/directory
- username and password that are necessary to access the configured directory path
  through SFTP. Username and password can be omitted in case the XML Director server (your
  Plone instance) has access using SSH keys (without passphrase) to the remote SFTP
  service. The handling of username + password vs. SSH authentication using SSH keys is
  currently under investigation and might change in a further release.



================    ==============  ======================
Protocol/Service    Native support  3rd-party SaaS support (e.g. Otixo.com, storagemadeeasy.com)
================    ==============  ======================
Local filesystem    Yes             No
WebDAV              Yes             Yes
ExistDB 2.2/3.0     Yes             Yes
BaseX 8.3           Yes             Yes
Amazon AWS S3       Yes             Yes
Alfresco            Yes             Yes
Owncloud            Yes             Yes
Dropbox             (experimental)  Yes
SFTP                (experimental)  Yes
FTP                 (experimental)  Yes
================    ==============  ======================

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

All releases and code changes to XML Director are automatically tested against
various combinations of Plone and backend versions. The current test setup
consists of 14 different combinations against the most common databases and
services. See
https://github.com/xml-director/xmldirector.plonecore/blob/master/.travis.yml
for testing details. A complete test run consists of over 1400 single tests. 

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

