import os
from setuptools import setup, find_packages

version = '0.1.11'

setup(name='zopyx.existdb',
      version=version,
      description="Plone-ExistDB integration",
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
      keywords='exist-db existdb Plone XML Python',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://pypi.python.org/pypi/zopyx.existdb',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zopyx', 'zopyx.existdb'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.directives.form',
          'hurry.filesize',
          'humanize',
          'zope.i18nmessageid',
          'plone.browserlayer',
          'plone.api',
          'fs',
          'dexml'
          # -*- Extra requirements: -*-
      ],
      tests_require=['zope.testing'],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

