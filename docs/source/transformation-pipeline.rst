Transformation pipelines - chaining transformations
===================================================

XML Director provides a mechanism for chaining registered
transformer operations in arbitrary order in order to process
an XML document through multiple steps. Recall that transformers
in XML Director are registered as tuple (``family``, ``transformer_name``).

The following example we will register two Python transformers that will 
modify the given sample XML document.

Example:

.. code-block:: python


    from xmldirector.plonecore.transformation import Transformer

    # the source XML document
    sample_xml = u'''
    <hello>
        <world>
            <foo>123</foo>
            <foo>345</foo>
            <foo>789</foo>
        </world>
        <umlaute>mit Umlauten üöäßÜÖÄ</umlaute>
    </hello>
    '''

    def python_transformer(root, conversion_context):
        """ Sample Python transformation turning all <foo>
            tags into <bar> tags.
        """

        for node in root.xpath('//foo'):
            node.tag = 'bar'


    def python_transformer2(root, conversion_context):
        """ Sample Python transformation removing all <foo>
            nodes and putting an attribute foo="bar" into
            the root node
        """
        for node in root.xpath('//foo'):
            node.getparent().remove(node)
        root.attrib['foo'] = 'bar'


    # Register both transformations
    registry = TransformerRegistry()
    registry.register_transformation('demo', 'trans1', python_transformer, 'python')
    registry.register_transformation('demo', 'trans2', python_transformer2, 'python')


Running the first ``trans1`` transformation (turning all <foo> tags into <bar> tags):

.. code-block:: python

    # Run transformation ``trans1`` only:
    T = Transformer([('demo', 'trans1')],
                    transformer_registry=registry)
    print T(sample_xml)

The transformation result is the following:

.. code-block:: xml

    <hello>
        <world>
            <bar>123</bar>
            <bar>345</bar>
            <bar>789</bar>
        </world>
        <umlaute>mit Umlauten üöäßÜÖÄ</umlaute>
    </hello>

Running the both transformations (removing all <foo> tags and placing an attribute foo="bar" into the root tag:

.. code-block:: python

    # Run transformation ``trans1`` only:
    T = Transformer([('demo', 'trans1'), ('demo', 'trans2')],
                    transformer_registry=registry)
    print T(sample_xml)


    # Define the transformation pipeline
    T = Transformer([('demo', 'trans1'),
                     ('demo', 'trans2)]
                    transformer_registry=registry)

and the result is:

.. code-block:: xml

    <hello foo="bar">
        <world>
        </world>
        <umlaute>mit Umlauten üöäßÜÖÄ</umlaute>
    </hello>


Mixing transformer steps
------------------------
It is totally fine to mix arbitrary transformer step in one pipline independent
of the underlaying implementation.  Keep in mind that XSLT1 transformations are
directly carried out on the Python level while XSLT2 and XSLT3 transformations
are executed externally using the Saxon parser. Due to its implementation in
Java there will be some performance loss since XML Director requires to start
Java for each Saxon call. 

