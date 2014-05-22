from setuptools import setup, find_packages
import os

version = '0.2.2'

setup(name='pp.client-plone',
      version=version,
      description="Produce & Publisher Plone Client Connector",
      long_description=open(os.path.join("docs", "source", "README.rst")).read() + "\n" +
                       open(os.path.join("docs", "source", "HISTORY.rst")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Zope2",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='PDF Plone Python EBook EPUB',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://pypi.python.org/pypi/pp.client-plone',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pp', 'pp.client', 'pp.client'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.browserlayer',
          'BeautifulSoup',
          'lxml',
          'Pillow',
          'cssutils',
          'pp.client-python',
          'pp.core',
          'archetypes.schemaextender',
          'unittest2'
          # -*- Extra requirements: -*-
      ],
      tests_require=['zope.testing'],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

