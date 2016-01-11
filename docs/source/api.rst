REST API
========

.. http:put:: /plone/xmldirector-create

   Create a new instance of XML Director ``Connector``

   **Example request**:

   .. sourcecode:: http

      PUT /xmldirector-create HTTP/1.1
      Host: example.com
      Accept: application/json
      Content-Type: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json

      {
        "id": "1f461181-b7cd-4708-8181-9787c9530ed2",
        "url": "http://example.com/plone/1f461181-b7cd-4708-8181-9787c9530ed2"
      }

   :reqheader Accept: must be ``application/json``
   :reqheader Content-Type: must be ``application/json``
   :reqheader Authorization: HTTP basic authentication
   :statuscode 201: content created
   :statuscode 403: unauthorized
   :statuscode 404: not found

.. http:get:: /xmldirector-search

   Search for connectors

   **Example request**:

   .. sourcecode:: http

      GET /plone/xmldirector-search HTTP/1.1
      Host: example.com
      Accept: application/json
      Content-Type: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json

      {u'items': [{u'created': u'2015-12-18T13:16:28+01:00',
                   u'creator': u'admin',
                   u'id': u'148d5f0a-3be9-42b6-bc2e-b128df2dbc1b',
                   u'modified': u'2015-12-18T13:16:28+01:00',
                   u'path': u'/plone/148d5f0a-3be9-42b6-bc2e-b128df2dbc1b',
                   u'title': u'',
                   u'url': u'http://localhost:55001/plone/148d5f0a-3be9-42b6-bc2e-b128df2dbc1b'},
                  {u'created': u'2015-12-18T13:16:27+01:00',
                   u'creator': u'god',
                   u'id': u'connector',
                   u'modified': u'2015-12-18T13:16:27+01:00',
                   u'path': u'/plone/connector',
                   u'title': u'',
                   u'url': u'http://localhost:55001/plone/connector'}]}

   :reqheader Accept: must be ``application/json``
   :reqheader Content-Type: must be ``application/json``
   :reqheader Authorization: HTTP basic authentication
   :statuscode 200: Search successful
   :statuscode 403: unauthorized
   :statuscode 404: not found

.. http:delete:: /xmldirector-delete

   Removes a ``Connector`` given by its path/url

   **Example request**:

   .. sourcecode:: http

      DELETE /plone/1f461181-b7cd-4708-8181-9787c9530ed2/xmldirector-delete HTTP/1.1
      Host: example.com
      Accept: application/json
      Content-Type: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json

      {
      }

   :reqheader Accept: must be ``application/json``
   :reqheader Content-Type: must be ``application/json``
   :reqheader Authorization: HTTP basic authentication
   :statuscode 200: Connector deleted
   :statuscode 403: unauthorized
   :statuscode 404: not found


.. http:POST:: /path-to-connector/xmldirector-set-metadata

   Set metadata for a ``Connector`` object. You can set the ``title``,
   ``description`` (both text) and the ``subject`` (list of strings)
   as metadata for every ``Connector`` object. In addition the ``custom``
   field can be used to specify arbitrary metadata that is not part
   of the official Plone metadata.

   **Example request**:



   .. sourcecode:: http

      POST /plone/some/path/xmldirector-set-metadata HTTP/1.1
      Host: example.com
      Accept: application/json
      Content-Type: application/json

      {
          "custom": {
              "a": 2, 
              "b": 42
          }, 
          "description": "my description", 
          "title": "hello world"
      }




   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json

      {
      }

   :reqheader Accept: must be ``application/json``
   :reqheader Content-Type: must be ``application/json``
   :reqheader Authorization: HTTP basic authentication
   :statuscode 200: Setting of metadata successful
   :statuscode 403: unauthorized
   :statuscode 404: not found


.. http:GET:: /path-to-connector/xmldirector-get-metadata

   Return Plone and custom metadata (see ``xmldirector-set-metadata`` for details.

   **Example request**:

   .. sourcecode:: http

      GET /plone/some/path/xmldirector-get-metadata HTTP/1.1
      Host: example.com
      Accept: application/json
      Content-Type: application/json



   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json

      {
          "custom": {
              "a": 2, 
              "b": 42
          }, 
          "description": "my description", 
          "title": "hello world"
      }

   :reqheader Accept: must be ``application/json``
   :reqheader Content-Type: must be ``application/json``
   :reqheader Authorization: HTTP basic authentication
   :statuscode 200: Get operation successful
   :statuscode 403: unauthorized
   :statuscode 404: not found

.. http:GET:: /path-to-connector/xmldirector-get
    
   Retrieve a single file by path.

   **Example request**:

   .. sourcecode:: http

      GET /plone/some/path/xmldirector-get?name=src/sample.docx HTTP/1.1
      Host: example.com
      Accept: application/json
      Content-Type: application/json


   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Disposition: attachment; filename=sample.docx'
      Content-Length: 89796
      Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document

      <binary data in response body>

   :query string name: name of file to be retrieved
   :reqheader Accept: must be ``application/json``
   :reqheader Content-Type: must be ``application/json``
   :reqheader Authorization: HTTP basic authentication
   :statuscode 200: Get operation successful
   :statuscode 403: unauthorized
   :statuscode 404: not found

.. http:GET:: /path-to-connector/xmldirector-get-zip
    
   Retrieve all files as ZIP file.

   **Example request**:

   .. sourcecode:: http

      GET /plone/some/path/xmldirector-get-zip HTTP/1.1
      Host: example.com
      Accept: application/json
      Content-Type: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Content-Disposition: attachment; filename=some-id.zip'
      Content-Length: 89796
      Content-Type: application/zip

      <binary ZIP data in response body>

   :reqheader Accept: must be ``application/json``
   :reqheader Content-Type: must be ``application/json``
   :reqheader Authorization: HTTP basic authentication
   :statuscode 200: Get operation successful
   :statuscode 403: unauthorized
   :statuscode 404: not found

.. http:POST:: /path-to-connector/xmldirector-store
    
   Upload one or more files as multipart form-data request.
   Please refer to https://en.wikipedia.org/wiki/MIME#Content-Type for details
   about multipart/form-data requests. You must specify the ``filename`` for each
   uploaded file. The ``filename`` might be a relative path which is preserved 
   upon storage. 
   
   .. note::
       All uploaded files will be stored on the server under the ``src``  
       subfolder. All uploaded files **must** use the same ``name`` parameter
       within the POST body (see example below)::

          name=files


   Example of ``filename`` mapping:

   - filename=some.png -> ``src/some.png``
   - filename=my/images/some.png -> ``src/my/images/some.png``

   XML Director will calculated a SHA256 has for all uploaded files and
   stores them internally for efficient retrieval. The hashes of uploaded
   files are exposed through the ``xmldirector-hashes`` and ``xmldirector-list-full``
   API methods.

   **Example request**:

   Uploaded files files ``a.txt`` and ``a.html`` will be stored as ``src/a.txt`` and ``src/a.html``.


   .. sourcecode:: http

      PUT /xmldirector-store HTTP/1.1
      Host: example.com
      Accept: application/json
      Content-Type: multipart/form-data; boundary=---------------------------9051914041544843365972754266
      Content-Length: 554
      
      -----------------------------9051914041544843365972754266
      Content-Disposition: form-data; name="files"; filename="a.txt"
      Content-Type: text/plain

      Content of a.txt.

      -----------------------------9051914041544843365972754266
      Content-Disposition: form-data; name="files"; filename="a.html"
      Content-Type: text/html

      <!DOCTYPE html><title>Content of a.html.</title>

      -----------------------------9051914041544843365972754266--


   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json
      
      {
      }

   :reqheader Accept: must be ``application/json``
   :reqheader Content-Type: must be ``multipart/form-data``
   :reqheader Authorization: HTTP basic authentication
   :statuscode 200: upload successful
   :statuscode 403: unauthorized
   :statuscode 404: not found



.. http:POST:: /path-to-connector/xmldirector-store-zip
    
   Upload one or more files as ZIP archive. The ZIP archive
   will be unpacked. The functionality is similar to ``xmldirector-store``.
   except that the uploaded ZIP archive must be uploaded with query parameter
   ``name=zipfile``. All unpacked files will be stored within the subfolder ``src``.
   directory names are being preserved.


.. http:GET:: /path-to-connector/xmldirector-list
   
   ``xmldirector-list`` retrieves list of all stored files. 

   **Example request**:

   .. sourcecode:: http

      GET /plone/path/to/object/xmldirector-list HTTP/1.1
      Host: example.com
      Accept: application/json
      Content-Type: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json

      {u'files': [u'src/folder/3.txt',
                  u'src/folder/1.txt',
                  u'src/folder/2.txt']
      }

   :reqheader Accept: must be ``application/json``
   :reqheader Content-Type: must be ``application/json``
   :reqheader Authorization: HTTP basic authentication
   :statuscode 200: Success
   :statuscode 403: unauthorized
   :statuscode 404: not found

   
.. http:GET:: /path-to-connector/xmldirector-list-full
   
   Retrieve a list of all stored files including information about size, file mode
   and their SHA256 hash.

   **Example request**:

   .. sourcecode:: http

      GET /plone/path/to/object/xmldirector-list-full HTTP/1.1
      Host: example.com
      Accept: application/json
      Content-Type: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json


      {u'src': {u'modified_time': u'2015-12-21T07:30:27', u'st_mode': 16832},
       u'src/folder': {u'modified_time': u'2015-12-21T07:30:27', u'st_mode': 16832},
       u'src/folder/1.txt': {u'modified_time': u'2015-12-21T07:30:27',
                             u'sha256': u'a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447',
                             u'size': 12,
                             u'st_mode': 33216},
       u'src/folder/2.txt': {u'modified_time': u'2015-12-21T07:30:27',
                             u'sha256': u'6355baea1348fe93f7d9c0c56a5cfeff34682aeb6f24a61ce7b06fdb94927a8d',
                             u'size': 24,
                             u'st_mode': 33216},
       u'src/folder/3.txt': {u'modified_time': u'2015-12-21T07:30:27',
                             u'sha256': u'a8e82d2a65f75a68e82ea8835522dd67f1fede950bfedef9ccd1b2608dd70cb5',
                             u'size': 20,
                             u'st_mode': 33216},
      }

   :reqheader Accept: must be ``application/json``
   :reqheader Content-Type: must be ``application/json``
   :reqheader Authorization: HTTP basic authentication
   :statuscode 200: Success
   :statuscode 403: unauthorized
   :statuscode 404: not found
   
.. http:GET:: /path-to-connector/xmldirector-hashes
   
   Return all SHA256 hashes of all stored files.
   and their SHA256 hash.

   **Example request**:

   .. sourcecode:: http

      GET /plone/path/to/object/xmldirector-hashes HTTP/1.1
      Host: example.com
      Accept: application/json
      Content-Type: application/json

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/json

      {u'src/folder/1.txt': {u'sha256': u'a948904f2f0f479b8f8197694b30184b0d2ed1c1cd2a1ec0fb85d299a192a447'},
       u'src/folder/2.txt': {u'sha256': u'6355baea1348fe93f7d9c0c56a5cfeff34682aeb6f24a61ce7b06fdb94927a8d'},
       u'src/folder/3.txt': {u'sha256': u'a8e82d2a65f75a68e82ea8835522dd67f1fede950bfedef9ccd1b2608dd70cb5'}}
      }

   :reqheader Accept: must be ``application/json``
   :reqheader Content-Type: must be ``application/json``
   :reqheader Authorization: HTTP basic authentication
   :statuscode 200: Success
   :statuscode 403: unauthorized
   :statuscode 404: not found

.. http:POST:: /path-to-connector/xmldirector-delete-content
   
   Delete one or more items from the storage...to be written

.. http:POST:: /path-to-connector/xmldirector-convert
   
   Start a synchronous conversion against the C-Rex web-service (www.c-rex.net).

   The request must contain a ``mapping`` rule set that specifies the files to be
   included with the ZIP file to be send to the C-Rex service. The ``mapping`` 
   mechanism allows you to transform the paths of files as they exist on the server
   into a different path with in the ZIP file. The mechanism is based on the idea
   of the Apache Rewrite module for rewriting incoming request URLs (see
   http://httpd.apache.org/docs/2.0/misc/rewriteguide.html for details).


   All regular expression groups (regular expression patterns grouped in ``(...)``
   parentheses relate to ``$1``, ``$2`` etc. within the target expression.

   **Example 1**

    A rule

    .. code-block:: text

      [ "src/(.*)", "$1" ]

    will include files within the ``src`` folder into the ZIP file and chop of
    the leading ``src`` directory:

    .. code-block:: text

      src/myfiles/foo.png -> myfiles/foo.png


   **Example 2**

    A rule

    .. code-block:: text

      [ "src/(.*)/word/(.*).docx", "$1/$2.docx" ]

    will map ``.docx`` files into a new hierarchy

    .. code-block:: text

      src/files/word/foo.docx     -> files/foo.docx
      src/morefiles/word/bar.docx -> morefiles/bar.docx

   **Example 3**

    A rule

    .. code-block:: text

      [ "src/(.*)/word/(.*).docx", "files/$2.docx" ]

    will map ``.docx`` files into a new hierarchy ``files``

    .. code-block:: text

      src/files/word/foo.docx     -> files/foo.docx
      src/morefiles/word/bar.docx -> files.docx

   C-Rex will return a ZIP file with the converted data. The ZIP file will be unpacked
   within the top-level ``current`` directory within the CMS. In addition the ZIP file
   is returned with the HTTP response.
   
   **Example request**:

   .. sourcecode:: http

      POST /plone/path/to/object/xmldirector-convert HTTP/1.1
      Host: example.com
      Accept: application/json
      Content-Type: application/json

      {
          "mapping": [
              [ "src/(.*)", "$1" ]
          ]
      }

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: application/zip

      <binary ZIP data>


   :reqheader Accept: must be ``application/json``
   :reqheader Content-Type: must be ``application/json``
   :reqheader Authorization: HTTP basic authentication
   :statuscode 200: Success
   :statuscode 403: unauthorized
   :statuscode 404: not found
   
