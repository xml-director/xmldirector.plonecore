XSLT Registry
=============

XML-Director contains a registry for XSLT stylesheets.
Stylesheets in XML-Director can be grouped together as a ``family``.
A stylesheet family registers a XSLT stylesheet under an arbitrary
name that can is used a key/reference for further operations.
In order to retrieve an XSLT stylesheet - in particular its compiled
transformation - from the XSLT registry you always need the ``family``
name and the registered ``stylesheet_name``.

Registering a stylesheet
------------------------

Example::

    import lxml.etree
    from zope.component import getUtility
    from xmldirector.plonecore.interfaces import IXSLTRegistry

    registry = getUtility(IXSLTRregistry)
    registry.register_stylesheet('demo', 'test-transformation', '/path/to/test.xslt')

The stylesheet registration will check for:

- duplicate stylesheet registrations (``family`` + ``stylesheet_name`` must be unique)
- XML validity of the stylesheet
- XSLT validity of the stylesheet  

  
Retrieving a stylesheet
-----------------------

Example::

    transformation = registry.get_stylesheet('demo', 'test-transformation')    
    doc_root = lxml.etree.fromstring(some_xml_string)
    result = transformation(doc_root)$
    html = lxml.etree.tostring(result.getroot(), encoding=unicode)$ 

Clearing the XSLT registry
--------------------------

Example::

    registry.clear()
    print len(registry) # returns 0

