Dexterity fields
================


``xmldirector.plonecore`` comes with the following Dexterity fields that
can be either used programmatically in your own field schema or through-the-web.

Example of a simple Dexterity-based content-type using all available fields::

    from zope.interface import implements
    from plone.dexterity.content import Item
    from plone.supermodel import model

    from xmldirector.plonecore.i18n import MessageFactory as _

    from xmldirector.plonecore.dx import dexterity_base
    from xmldirector.plonecore.dx.xml_binary import XMLBinary
    from xmldirector.plonecore.dx.xml_image import XMLImage
    from xmldirector.plonecore.dx.xml_field import XMLText
    from xmldirector.plonecore.dx.xpath_field import XMLXPath


    class IXMLDocument(model.Schema):

        xml_content = XMLText(
            title=_(u'XML Content'),
            required=False
        )

        xml_xpath = XMLXPath(
            title=_(u'XML XPath expression'),
            description=_(u'Format: field=<fieldname>,xpath=<xpath expression>'),
            required=False
        )

        xml_binary = XMLBinary(
            title=_(u'XML Binary'),
            required=False
        )

        xml_image = XMLImage(
            title=_(u'XML Image'),
            required=False
        )


    class XMLDocument(Item, dexterity_base.Mixin):

        implements(IXMLDocument)


XMLText
-------

The ``XMLText`` can be used to store *valid* XML content. The field is rendered
without Plone using the ACE editor. You can perform a client-side XML validation
within the edit mode of a document by clicking on the ``Validate XML`` button.
A document with invalid XML content can not be submitted or saved. Invalid XML
will be rejected with an error message through the edit form.

XMLXPath
--------

The ``XMLXPath`` field can be used to reference an ``XMLText`` field in order
to display a part of the XML content using an XPath expression.

Example

An ``XMLPath`` field with field name ``myxml`` might contain the following XML
content::

    <?xml version="1.0"?>
    <doc>
        <metadata>
            <title>This is a text</title>
        </metdata>
        <body>....</body>
    </doc>

In order to extract and display the <title> text within a dedicated Dexterity field
you can use the following extended expression::

    field=<fieldname>,xpath=<xpath expression>

In this case you would use::

    field=myxml,xpath=/doc/metadata/title/text()

Note that the current syntax is very rigid and does not allow any whitespace
characters expect within the <xpath expression>.


XMLBinary, XMLImage
-------------------
Same as file and image field in Plone but with BaseX or eXist-db as
storage layer.


API for setting and getting XML field values
--------------------------------------------

The values of XML fields are managed through dedicated API methods ``xml_get()`` and ``xml_set()``.
This is inconsistent with the standard Dexterity approach to set/get directly on the objects or
through behaviors. Unfortunately Dexterity has no concept of a storage layer and in order to provide
a consistent and explicit API it was necessary to invent our own API for the XML fields of
``xmldirector.plonecore``.


Manipulating XMLText fields
+++++++++++++++++++++++++++

Storing XML data and retriving is pretty trivial. And XML string to be stored must
be either given as UTF-8 encoded byte string or as Python unicode string (without
the XML premable)::

    xml = """<xml? version="1.0"?>
             <example>data</example>
          """
    # Store XML
    my_doc.xml_set('xml_content', xml)

    # Read XML
    xml2 = my_doc.xml_get('xml_content')


Manipulating XMLPath fields
+++++++++++++++++++++++++++

The following example shows how to retrieve parts of an XML document
through an XPath field::

    xml = "<xml? version="1.0"?>
             <example>
                <title>Hello world/title>
                <value>a</value>
                <value>b</value>
                <value>c</value>
             </example>
          "

    # Store XML
    my_doc.xml_set('xml_content', xml)

    # Create an Xpath expression for the retrieving the title
    my_doc.xml_set('xml_xpath', 'field=xml_content,xpath=//title/text()')
    result = my_doc.xml_get('xml_xpath)
    # result = [u'Hello world']

    # Create an Xpath expression for all <value> values
    my_doc.xml_set('xml_xpath', 'field=xml_content,xpath=//value/text()')
    result = my_doc.xml_get('xml_xpath)
    # result = [u'a', u'b', u'c']

Manipulating XMLImage fields
++++++++++++++++++++++++++++

For storing image data on an ``XMLImage`` field, the image data must be encapsulated
as an instance of ``plone.namedfile.NamedImage``::

    from plone.namedfile import NamedImage

    # storing image data
    named_image = NamedImage()
    named_image.data = img_data
    named_image.filename = u'test.jpg'
    named_image.contentType = 'image/jpg'
    my_doc.xml_set('xml_image', named_image)

    # retrieving image data
    result = my_doc.xml_get('xml_image')
    img_data = result.data            # binary image data
    filename = result.filename        # 'test.jpg'
    mimetype = result.contentType     # 'image/jpg'

    
Manipulating XMLBinary fields
+++++++++++++++++++++++++++++

For storing binary data on an ``XMLBinary`` field, the binary data must be encapsulated
as an instance of ``plone.namedfile.NamedFile``::

    from plone.namedfile import NamedFile

    # storing image data
    named_file= NamedFile()
    named_file.data = file_data
    named_file.filename = u'some.pdf'
    named_file.contentType = 'application/pdf'
    my_doc.xml_set('xml_binary', named_file)

    # retrieving binary data
    result = my_doc.xml_get('xml_binary')
    img_data = result.data            # binary data
    filename = result.filename        # 'some.pdf'
    mimetype = result.contentType     # 'application/pdf'
