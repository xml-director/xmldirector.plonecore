zopyx.existdb
=============

``zopyx.existdb`` integrates  Plone 4.3 and higher with 
eXist-db providing the following features:

- mounts an arbitary eXist-db collection into Plone
- indexing support (limited to one content document per Connector  
  instance)
- ACE editor integration
- ZIP export from eXist-db
- ZIP import into eXist-db

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


Author
------
| Andreas Jung/ZOPYX
| Hundskapfklinge 33
| D-72074 Tuebingen, Germany
| info@zopyx.com
| www.zopyx.com




