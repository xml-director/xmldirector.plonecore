Testing
=======

The ``xmldirector.plonecore`` functionality uses unit tests
and functional tests for testing the functionality of the software.

Running all tests
-----------------

The following command will run all tests against the pre-configured
eXist-db database.

.. code:: bash

    bin/test xmldirector.plonecore

For running all tests against eXist-db and Base-X use the following command

.. code:: bash

   bash test_all.sh

The testrunner respects the following environment variables that specify
the database backend to be used for the tests:

- ``CONNECTOR_URL`` - URL of the webdav service 
- ``CONNECTOR_USERNAME`` - Username to be used for authentication against the webdav service 
- ``CONNECTOR_PASSWORD`` - Password to be used for authentication against the webdav service

