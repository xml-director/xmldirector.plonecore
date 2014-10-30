Changelog
=========

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
