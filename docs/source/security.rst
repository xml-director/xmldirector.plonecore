Security 
========

XML Director itself is directly based on the ``Plone`` content management system
which counts as a very safe and secure CMS and has a great security record
for almost 15 years.

XML security
------------

XML Director tries its best to deal with attacks caused by XML data.  All
incoming data is parsed and verified against the most common XML attack vectors
like exponantial entity expansion or external entity expansion.  The XML
protection is based on the ``defusedxml`` module
(https://pypi.python.org/pypi/defusedxml).

Resources
---------

- https://en.wikipedia.org/wiki/Billion_laughs
- https://www.owasp.org/index.php/XML_External_Entity_(XXE)_Processing
- https://pypi.python.org/pypi/defusedxml
