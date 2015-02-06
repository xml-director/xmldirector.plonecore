Validator Registry
==================

XML-Director provides a registry for registering validators.
The registry supports the following validation methods:

- XML schemas (file suffix ``.xsd``)
- Document Type Definitions DTD (file suffix ``.dtd``)
- RelaxNG schemas (file suffix ``.rng``)
- Schematron (file suffix ``.sch``)

Validators in XML-Director can be grouped together as a ``family``.
A family is a list of validators that belongs together (per project, per 
publication etc.) - the semantics is left of the user of XML-Director.
The default method for registering one or multiple validators is by putting
them into a folder and calling the ``parser_folder()`` API of the validator 
registry. The type of a validator is derived from its file extension.

The validator registry supports both local and remote directories (WebDAV,
SFTPFS, FTP etc.).


Registering a folder with validator files
-----------------------------------------

Example::

    from xmldirector.plonecore.validator_registry import ValidatorRegistryUtility

    # local filesystem
    ValidatorRegistryUtility.parse_folder(
        family='myproject',
        directory='/path/to/my/schema')

    # WebDAV filesystem (e.g. Base-X or eXist-db)
    ValidatorRegistryUtility.parse_folder(
        family='myproject',
        directory='dav://username:password@myhost:port/exist/webdav/db/schemas')

    # FTP server 
    ValidatorRegistryUtility.parse_folder(
        family='myproject',
        directory='ftp://ftp.customer.com/public/schemas')


Verifying XML content against a validator
-----------------------------------------

Example::

    from zope.component import getUtility
    from xmldirector.plonecore.interfaces import IValidatorRegistry

    registry = getUtility(IValidatorRegistry)
    validator = registry.get_validator('myproject', 'some.xsd')
    result = validator.validate(some_xml)
    if result: 
        print 'XML validates against given schema'
    else:
        for error in result.errors:
            print error

The ``result`` object will evaluate to ``True`` in case of a validation with
out errors.  Otherwise ``result`` will result to ``False``. The attribute
``errors`` holds a list of error messages related to the validation errors.


Viewing all registered validators
---------------------------------

XML-Director implements a view ``@@validator-registry`` for the Plone root folder 
for introspecting the validator registry. The view lists all validators together with
information about family, validator name, type of validator and its filesystem path.    

Example::

    http://host:port/path/to/plone@@validator-registry
