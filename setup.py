import os
from setuptools import setup, find_packages
version = '0.1.0'
README = os.path.join(os.path.dirname(__file__), 'README')
long_description = open(README).read()
setup(name='fs',
      version=version,
      description=("Easier filehandling for Python."),
      long_description=long_description,
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities'],
      keywords='fs filesystem file files filehandling',
      author='Stijn Debrouwere',
      author_email='stijn@stdout.be',
      url='http://stdbrouw.github.com/python-fs/',
      download_url='http://www.github.com/stdbrouw/python-fs/tarball/master',
      license='MIT',
      packages=find_packages(),
      )
