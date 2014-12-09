
xmldirector.plonecore
=====================

.. note:: This module  

  - *is not* a replacement for the ZODB or any other Plone storage (never was, never will)
  - *is not* a storage layer for Archetypes or Dexterity content (never was, never will)
  - *is* a solution for mounting XML databases like eXist-db or
    BaseX into Plone through their WebDAV port
  - *is* an _experimental_ solution for mounting general WebDAV 
    services into Plone

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

The primary usecase for ``xmldirector.plonecore`` is the integration of XML document
collections into Plone using eXist-db as storage layer. ``xmldirector.plonecore`` is
not storage layer for Plone content in the first place although it could be
used in some way for storing primary Plone content (or parts of the content)
inside eXist-db. There is no build-in support for mapping metadata as stored in
XML documents to Plone metadata or vice versa. However this could be
implemented easily in application specific code build on top of
``xmldirector.plonecore``. The design goal of ``xmldirector.plonecore`` is to provide the basic
functionality for integrating Plone with eXist-db without implementing any
further specific application requirements.  Additional functionality can be
added through Dexterity behaviors, supplementary browser views, event lifecycle
subscribers and related technology.

Installation
------------

Add ``xmldirector.plonecore`` to the ``eggs`` and ``zcml`` options of your buildout
configuration, re-run buildout and install the connector through the add-ons
management of Plone.

Configuration
-------------

Goto the Plone control panel and click on the ``Exist-DB`` configlet and
configure the 

- eXist-db server webdav url e.g. ``http://localhost:6080/existdb/webdav/db``

  The eXist-db subpath ``/exist/webdav/db`` will be added internally.

- eXist-db username

- eXist-db password

- eXist-db emulation mode. Set the emulation mode to ``webdav`` for the integration of
  arbitrary WebDAV services.


Using xmldirector.plonecore
-------------------
The package provides a new content-types ``Connector`` that will include
eXist-db into Plone - either from the top-level collection of your eXist-db
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

License
-------
This package is published under the GNU Public License V2 (GPL 2)

Source code
-----------
See https://github.com/xml-director/xmldirector.plonecore

Bugtracker
----------
See https://github.com/xml-director/xmldirector.plonecore/issues

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

