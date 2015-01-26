Changelog
=========

0.3.5 (unreleased)
------------------
- rewritten persistent logger internals: now uses an OOBTree
  for holding all logging entries instead of a persistent list
  in order to support filtering of log entries by min-max 
  values
- logger table now uses a paginated view with searchable columns
- webdav password setting is no longer required (empty password allowed)
- fixed Webdav authentication issue with empty passwords

0.3.4 (2015-01-13)
------------------

- default view handler accept a custom request/filename
  argument in order to override the name of downloaded file
- fixed bug in view registry with BrowserView as view handler
- added PersistentLoggerAdapter for adopting arbitrary
  persistent objects for persistent logging through a Zope
  annotation  

0.3.3 (2015-01-05)
------------------

- running the tests should not leave any testing directory
  traces within the XML databases 
- almost 100% test coverage for the core functionality
- more tests
- added documentation on content-types

0.3.2 (2014-12-30)
------------------

- SHA256 calculation for xml content now generated in 
  a more stable way (but possibly much slower way)
- API for service-side XML validation
- added Docker support
- added XSLT registry
- added Shakespeare XML data for XMLDocument demo content-type
- added 'test_all.sh' script for running tests against BaseX 
  and eXist-db Docker containers 

0.3.1 (2014-12-12)
------------------
- added ``Test connection`` button to controlpanel
- moved test content type into a dedicated profile
  ``democontent``
- Moved metadata handling from JSON to XML on the storage
  layer in order to let the underlaying database index
  the .metadata.xml files as well

0.3.0 (2014-12-11)
------------------

- renamed zopyx.existdb to xmldirector.plonecore
- experimental Dexterity support with four new fields:

  - XMLText - for XML content
  - XMLXPath - for referencing XMLText parts through an XPath 
    expression
  - XMLImage and XMLBinary - same as image and file fields in Dexterity
    but with eXist-db as storage layer

- removed ``emulation`` configuration option
- added plone.app.dexterity as dependency
- upgraded to ACE editor V 1.1.8
- added progressbar for zip_upload()
- added support for importing a single file through the 
  ZIP import form into the current subdirectory

0.2.11 (2014-11-08)
-------------------
- updated documentation

0.2.10 (2014-11-08)
-------------------
- bugfix release

0.2.9 (2014-11-01)
------------------
- support for overriding credentials locally 

0.2.8 (2014-11-01)
------------------
- minor fix for mounting Plone sites over WebDAV into another Plone site

0.2.7 (2014-11-01)
------------------
- experimental support for BaseX XML database through the WebDAV API.
  Limitations: REMOVE operations over WebDAV do not seem to work 
  against BaseX 7.9


0.2.6 (2014-11-01)
------------------
- more tests

0.2.5 (2014-10-30)
------------------
- experimental traversal support for accessing WebDAV resources by path
  using (un)restrictedTraverse()
- minor URL fixes
- more tests  

0.2.4 (2014-10-22)
-------------------
- configuration option for default view for authenticated site visitors


0.2.3 (2014-10-13)
-------------------
- fix in saving ACE editor content

0.2.2 (2014-10-12)
-------------------
- typo in page template

0.2.1 (2014-10-12)
-------------------

- added support for renaming a collection through the web

0.2.0 (2014-10-02)
-------------------

- various minor bug fixes
- added basic tests 

0.1.17 (2014-09-25)
-------------------

- fixed action links


0.1.16 (2014-09-25)
-------------------

- Connector is no longer a folderish object

0.1.15 (2014-09-22)
-------------------

- removed indexing support completely (leaving a specific
  indexing functionality to policy packages using zopyx.existdb)

0.1.14 (2014-09-15)
-------------------

- fixed subpath handling in create/remove collections

0.1.13 (2014-09-07)
-------------------
- support for removing collections TTW

0.1.12 (2014-09-05)
-------------------
- support for creating new collections TTW

0.1.11 (2014-08-21)
-------------------
- action "Clear log" added 

0.1.10 (2014-08-05)
-------------------
- log() got a new 'details' parameter for adding extensive logging information

0.1.9 (2014-08-01)
------------------
- human readable timestamps

0.1.8 (2014-07-31)
------------------
- minor visual changes

0.1.7 (2014-07-29)
------------------
- rewritten code exist-db browser code (dealing the correct
  way with paths, filenames etc.)

0.1.6 (2014-07-29)
------------------
- fixed improper view prefix in directory browser

0.1.5 (2014-07-13)
------------------
- minor fixes and cleanup

0.1.4 (2014-07-12)
------------------
- made webservice query API aware of all output formats (xml, html, json) 
  
- timezone handling: using environment variable TZ for converting eXist-db UTC
  timestamps to the TZ timezone (or UTC as default) for display purposes with
  Plone

0.1.3 (2014-07-07)
------------------
- added webservice API interface
- various bug fixes

0.1.2 (2014-06-30)
------------------
- various bug fixes

0.1.0 (2014-06-20)
------------------
- initial release
