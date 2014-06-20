Installation
============

This documentation assumes that your installation of Plone/Zope is based on
zc.buildout.


- edit your *buildout.cfg* -  add *pp.client-plone* to the 
  **eggs** options of your buildout.cfg::

    eggs = ...
        pp.client-plone

- restart Zope/Plone

- When running the Produce & Publish server on a different server, you must
  adjust the ``PP_SERVER`` environment variables within your *.bashrc* file (or
  a similar file) or you put those variables into your buildout configuration
  using the *<environment>* section.  Username and password are only needed
  when you run the Produce & Publish server behind a reverse proxy (requiring
  authentcation)::

    export PP_SERVER=http://user:password@your.server:6543/api/1

  or::

    <environment>
        PP_SERVER=http://user:password@your.server:6543/api/1
    </environment>

.. note:: This version of the Produce & Publish Plone Client Connector
    requires an installation of the new ``pp.server`` Produce & Publish Server.
    It will not work with the older ``zopyx.smartprintng.server`` server implementation.


Supported Plone content-types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Archetypes-based content-types
++++++++++++++++++++++++++++++

- Document
- Folder (nested structure)
- News item
- Collection (new-style collections Plone 4.3 only)
- Image

Dexterity-based content-types
+++++++++++++++++++++++++++++

There is no direct support for Dexterity content-types available however the
configuration contains an example configuration on how to register the
interface of a Dexterity content-type with the Plone Client Connector. However
support for Dexterity types will only work for filesystem-based Dexterity types
with a related marker interface - there is no support for through-the-web
defined Dexterity types.

Usage
~~~~~

The Plone connector provides a dedicated @@asPDF view that can
be added to the URL of any of the supported content-types of Plone
(Document, Folder, Newsitem, PloneGlossary). So when your document
is for example associated with the URL::

::

    http://your.server/plone/my-page

you can generate a PDF by using the URL

::

    http://your.server/plone/my-page/@@asPDF

Parameters
~~~~~~~~~~

The @@asPDF view accepts the following parameters controlling
certain aspects of the PDF conversion:

-  **language** - can be set to 'de', 'en', 'fr' etc. in order to
   control language-specific aspects of the PDF conversion. Most
   important: this parameter controls the hyphenation. The Plone
   connector comes out-of-the-box with hypenation tables for several
   languages.  You can omit this URL parameter if the **Language**
   metadata parameter (of the top-level document) to be converted is
   set within Plone.

-  **converter** - if you are using the Produce & Publish server
   with a converter backend other than PrinceXML you can specify a
   different name (default is *princexml*). Possible values

   - ``princexml``
   - ``pdfreactor``
   - ``phantomjs``

- **resource** - can be set in order to specify a registered resource
  directory to be used for  running the conversion. The ```resource``
  parameter must be identical with the ``name`` parameter of
  the related ZCML ``<pp:resourceDirectory>`` directive.

- **template**  - can be used to specify the name of template to be
  used for running the conversion. The ``template`` parameter usually
  refers to a .pt filename inside the ``resource`` directory.  

Miscellaneous
~~~~~~~~~~~~~

The environment varialble ``PP_ZIP_OUTPUT`` can be set to export
all resources used for the conversion into a ZIP file for debugging purposes.
The path of the generated ZIP file is logged within the standard Zope/Plone
logfile (or the console if Plone is running in foreground).
