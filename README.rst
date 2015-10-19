xmldirector.plonecore
=====================

.. image:: docs/source/images/xml-director-logo.jpg
            :width: 500

``xmldirector.plonecore`` is the technical foundation of the XML-Director
project (www.xml-director.info). The goal of the XML-Director project is
building an enterprise-level XML content management system on top of the CMS
Plone (www.plone.org) with support for XML databases like eXis-db or Base-X.
However the underlaying implementation can also be used to mount arbitrary
backend through WebDAV into Plone.


Build status
------------

See https://travis-ci.org/xml-director/xmldirector.plonecore

.. image:: https://travis-ci.org/xml-director/xmldirector.plonecore.svg?branch=master
    :target: https://travis-ci.org/xml-director/xmldirector.plonecore

.. note:: This module  

  - *is* a solution for mounting XML databases like eXist-db or
    BaseX into Plone through their WebDAV port
  - *is* a solution for construction Dexterity content-types programmatically
    or through-the-web with XML related fields where the content is stored
    in BaseX or eXist-db
  - *is* an _experimental_ solution for mounting general WebDAV 
    services into Plone
  - *is not* a replacement for the ZODB or any other Plone storage (never was, never will)

``xmldirector.plonecore`` integrates  Plone 4.3 and higher with 
eXist-db providing the following features:

- mounts an arbitary eXist-db collection into Plone
- ACE editor integration
- ZIP export from eXist-db
- ZIP import into eXist-db
- pluggable view mechanism for configuring custom views for XML database  
  content by filename and view name
- create, rename or delete collections through the web
- extensible architecture through Plone Dexterity behaviors
- support for XQuery scripts called through the RESTXQ layer of eXist-db
  (allows you to call XQuery scripts and return the output format (JSON,
  HTML, XML) depending on your application requirements)
- dedicated per-connector logging facility
- small and extensible
- experimental support for mounting arbitrary WebDAV service into Plone (set
  the emulation mode to ``webdav`` in the eXist-db control panel of Plone)
- Dexerity fields:

  - ``XMLText`` - a field for storing XML content in BaseX or eXist-db

  - ``XPathField`` - for retrieving parts of XML content stored within a 
    ``XMLText`` field through an XPath expression (e.g. for extracting
    and displaying metadata from XML content)

  - ``XMLBinary`` and ``XMLImage`` fields for storing binary data and images
    in BaseX or eXist-db. The functionality is identical with the standard
    Dexterity file and image fields (except for the different storage layer)



Full documentation 
------------------

See https://pythonhosted.org/xmldirector.plonecore/
