Changelog
=========

2.0.0 (2016-08-18)
------------------------
- full compatibility with Plone 5.0 (limited to Plone 5.1 alpha)
- replaced DataTables.net with agGrid
- major UI changes
- updated to latest ACE version
- switch to Dropzone.js for multi-file uploads

1.6.1 (2016-04-08)
------------------
- improved unicode filename handling across drivers
- PEP8 fixes

1.6.0 (2016-03-18)
------------------
- experimental native Dropbox support (requires installed 'dropbox' SDK for
  Python using 'pip install dropbox' or by adding 'dropbox' as dependency
  inside your buildout) - not ready for production
- workaround for sporadic open() failures with Exist-DB: 
  open() will be tried up to three times (with a slight delay between
  calls in order to give the backend a chance to recover in between)
- support for latest plone.api releases (which minor monkey patch)
- move restapi permission checks to ZCML configuration
- updated to ACE 1.2.3
- updated to DataTables 1.10.11
- support for latest plone.api release

1.5.0 (2016-02-17)
--------------------

- huge internal renaming: renamed all webdav_* variables
  to connector_* 
- adjusted tests to Marc Logic Server

1.4.2 (2016-02-02)
--------------------

- fix in restapi in the context of local fs tests


1.4.1 (2016-01-18)
--------------------

- pass query string down to redirection call within __call__()

1.4.0 (2016-01-11)
--------------------
- new REST API

1.3.0 (2015-12-20)
--------------------
- added 'create_if_not_existing' parameter to webdav_handle() method
- added ensuredir() to wrapper base class

1.3.0b1 (2015-10-15)
--------------------

- support for OSFS (local filesystem), S3
- individual per-connector URL configuration
- support for multi-file uploads  
- unicode fixes in the context of testing federated cloud solutions
- massive amount of smaller internal and UI fixes
- lots of testing with different storage backends
- updated tests

1.2.0 (2015-09-29)
------------------

- refactored zip export functionality
- new supported WebDAV storage backends:
  
  - Alfresco
  - Owncloud
  - Dropbox (via dropdav.com SaaS) 

1.1.1 (2015-08-25) 
------------------

- updated selenium version pin
- better encapsulation of the DataTables Javascript initialization
  code in local.js
- fixed integration bug in Plone 5.0

1.1.0 (2015-08-21)
------------------

- some CSS styles fine-tuning
- added optional ``dirs`` parameter to ZIP export API for 
  exporting only a subset of the export directory structure
- added control panel functionality for installing Exist-DB
  specific RESTXQ script (e.g. all-locks.xql which is needed
  by the lockmanager introspection control panel for getting
  hold of all locks).
- ZIP import now works inside the given subdirectory and no longer
  only on the top level directory of the connector
- delete actions for collections and collection items
- delete actions now ask for confirmation
- massive speedup of ZIP import by reducing and caching WebDAV operations
- using Datatables.net for collections and collection items
- ZIP export/import is now more robust with directories or filenames
  containing non-ascii characters
- improved Plone 5.0 integration

1.0.4 (2015-07-22)
------------------

- updated ACeditor to version 1.2.0


1.0.3 (2015-07-22)
------------------

- using DataTables.net for connector logging view instead of TableUtils JS

1.0.2 (2015-06-12)
------------------

- updated Saxon 6.0.6HE
- added get_last_user(), get_last_date() to logger API for
  getting hold of the username performing the last logger entry

1.0.0 (2015-05-30)
------------------
- using defusedxml module for protecting XML Director against
  malicious data and XML related security attacks
- added support for 'force_default_view' URL parameter 
  to enforce redirection to the default anonymous view
- support for logging HTML messages

0.4.2 (2015-04-11)
------------------
- updated lxml, cssselect dependencies to newest versions
- analyzed XSD parsing slowness and logging/warning long-running
  XSD parsing
- first serious take on Plone 5.0 compatibility on the UI level
  (backend tests have been always passing but we had serious
  UI issues until 5.0 beta 1 and there are still issues). Plone 5
  beta support is work-in-progress and not fully completed.

0.4.1 (2015-04-07)
------------------
- added entry_by_uuid() to PersistentLogAdapter API
- fixed unicode issues with uploaded binaries/images with non-ascii 
  filenames
- added 'version_suffix' parameter to parser_folder() of validator registry
- Javascript cleanup

0.4.0 (2015-02-18)
------------------
- added @@transformer-registery view
- added @@transformer-registery-view view
- updated xmldirector.demo to use Transformer registry
- added (optional) debug option for debugging Transformer steps (input and
  output data of a step is written to disk)
- added more tests
- support for XSLT2+3 transformations by integrating Saxon 9.6 HE


0.3.6 (2015-02-06)
------------------
- re-added Dexterity tests
- added validator registry for XML schemas, DTDs, Schematron files
  and RelaxNG schemas
- added @@validator-registry view
- added unified validation API based on registered validation files
- documented validator registry

0.3.5 (2015-01-30)
------------------
- rewritten persistent logger internals: now uses an OOBTree
  for holding all logging entries instead of a persistent list
  in order to support filtering of log entries by min-max 
  values
- logger table now uses a paginated view with searchable columns
- webdav password setting is no longer required (empty password allowed)
- fixed Webdav authentication issue with empty passwords
- moved demo related code into a dedicated package xmldirector.demo

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
