zopyx.existdb
=============

``zopyx.existdb`` integrates  Plone 4.3 and higher with 
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

The primary usecase for ``zopyx.existdb`` is the integration of XML document
collections into Plone using eXist-db as storage layer. ``zopyx.existdb`` is
not storage layer for Plone content in the first place although it could be
used in some way for storing primary Plone content (or parts of the content)
inside eXist-db. There is no build-in support for mapping metadata as stored in
XML documents to Plone metadata or vice versa. However this could be
implemented easily in application specific code build on top of
``zopyx.existdb``. The design goal of ``zopyx.existdb`` is to provide the basic
functionality for integrating Plone with eXist-db without implementing any
further specific application requirements.  Additional functionality can be
added through Dexterity behaviors, supplementary browser views, event lifecycle
subscribers and related technology.

Installation
------------

Add ``zopyx.existdb`` to the ``eggs`` and ``zcml`` options of your buildout
configuration, re-run buildout and install the connector through the add-ons
management of Plone.

Configuration
-------------

Goto the Plone control panel and click on the ``Exist-DB`` configlet and
configure the 

- eXist-db server url e.g. ``http://localhost:6080``
- eXist-db username
- eXist-db password

Using zopyx.existdb
-------------------
The package provides a new content-types ``Connector`` that will include
eXist-db into Plone - either from the top-level collection of your eXist-db
database or from a subcollection. You can browse and traverse into
subcollections, view single documents or edit text-ish content through the web
(using the build-in ACE editor integration).

License
-------
This package is published under the GNU Public License V2 (GPL 2)

Source code
-----------
See https://bitbucket.org/onkopedia/zopyx.existdb

Bugtracker
----------
See https://bitbucket.org/onkopedia/zopyx.existdb

Credits
-------
The development of ``zopyx.existdb`` was funded as part of a customer project
by Deutsche Gesellschaft für Hämatologie und medizinische Onkologie (DGHO).


Author
------
| Andreas Jung/ZOPYX
| Hundskapfklinge 33
| D-72074 Tuebingen, Germany
| info@zopyx.com
| www.zopyx.com

