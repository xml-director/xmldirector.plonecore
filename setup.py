import os
from setuptools import setup, find_packages

version = '1.2.0'

setup(name='xmldirector.plonecore',
      version=version,
      description="XML-Director ",
      long_description=open(os.path.join("docs", "source", "README.rst")).read() + "\n" +
      open(os.path.join("docs", "source", "HISTORY.rst")).read(),
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Plone",
          "Framework :: Plone :: 4.3",
          "Framework :: Plone :: 5.0",
          "Framework :: Zope2",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='xml-director exist-db basex owncloud alfresco existdb Plone XML Python WebDAV',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://pypi.python.org/pypi/xmldirector.plonecore',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['xmldirector'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity',
          'plone.directives.form',
          'hurry.filesize',
          'humanize',
          'zope.i18nmessageid',
          'plone.browserlayer',
          'plone.api',
          'requests',
          'progressbar',
          'python-dateutil',
          'fs',
          'dexml',
          'grampg',
          'defusedxml',
          'cssselect',
          # -*- Extra requirements: -*-
      ],
      tests_require=['zope.testing'],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
