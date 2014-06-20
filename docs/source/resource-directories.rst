Resource directories
====================

The Plone Client connector allows you to define your own resource directories
containing

-  the PDF main template
-  style sheets
-  font files
-  hyphenation files

Registering your own resource directory
---------------------------------------

First you need your own policy - e.g. *zopyx.theme*. Inside the configure.zcml
file of your *zopyx.theme* you need to register a sub-directory using the
``pp:resourceDirectory`` directive:

::

    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:zcml="http://namespaces.zope.org/zcml"
        xmlns:pp="http://namespaces.zopyx.com/pp"
        >
    
        <pp:resourceDirectory
          name="zopyx_resource"
          directory="resources_pdf"
          />
    
    </configure>

The registered ``resources_pdf`` directory must contain all resource files as
flat structure (no sub-directories). The ``name`` parameter relates to the 
optional ``resource`` URL parameter as use for the ``@@asPlainPDF`` browser 
view.

Naming conventions
------------------

- PDF template: .pt
- Stylesheets: .css, .styles
- Images: .gif, .jpg, .png
- Hyphenation files: .hyp
- Coverpage templates (only used with Authoring Environment): .cover
- Font files: .otf, .ttf
