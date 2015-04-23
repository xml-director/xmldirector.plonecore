Transformer Registry
====================

XML-Director contains a registry for transformations.

Transformations in XML-Director can be grouped together as a ``family``.  A
transformer family registers a transformation  under an arbitrary name that can
is used a key/reference for further operations.  In order to retrieve an
transformation from the transformer registry you always need the ``family``
name and the name of the transformation.

The transformer registry supports current the following transformations:

- ``XSLT1`` - XSLT 1 stylesheets executed inside Python using libxml2
- ``XSLT2`` - XSLT 2 stylesheets executed through Saxon 9.6HE
- ``XSLT3`` - XSLT 3 stylesheets executed through Saxon 9.6HE
- ``python`` - arbitrary Python methods that work on the given node tree

Registering a transformer
-------------------------

Example::

    import lxml.etree
    from zope.component import getUtility
    from xmldirector.plonecore.interfaces import ITransformerRegistry

    registry = getUtility(ITransformerregistry)
    registry.register_transformer('demo', 'test-transformation', '/path/to/test.xsl', 'XSLT1')

The transformer registration will check for:

- duplicate stylesheet registrations (``family`` + ``stylesheet_name`` must be unique)
- XML validity of the stylesheet
- XSLT validity of the stylesheet 

  
Retrieving a transformation
---------------------------

Example::

    transformation = registry.get_transformation('demo', 'test-transformation')    
    doc_root = defused.xml.fromstring(some_xml_string)
    result = transformation(doc_root)$
    html = lxml.etree.tostring(result.getroot(), encoding=unicode)$ 

Clearing the transformer registry
---------------------------------

Example::

    registry.clear()
    print len(registry) # returns 0

