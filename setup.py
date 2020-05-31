"""Setup."""

import pepperoni
import setuptools


name = pepperoni.__name__
version = pepperoni.__version__
author = pepperoni.__author__
author_email = pepperoni.__email__
description = pepperoni.__doc__.splitlines()[0]
long_description = open('README.md', 'r').read()
long_description_content_type = 'text/markdown'
license = pepperoni.__license__
url = 'https://github.com/t3eHawk/pepperoni'
install_requires = ['sqlalchemy']
packages = setuptools.find_packages()
classifiers = ['Programming Language :: Python :: 3',
               'License :: OSI Approved :: MIT License',
               'Operating System :: OS Independent']


setuptools.setup(name=name,
                 version=version,
                 author=author,
                 author_email=author_email,
                 description=description,
                 long_description=long_description,
                 long_description_content_type=long_description_content_type,
                 license=license,
                 url=url,
                 install_requires=install_requires,
                 packages=packages,
                 classifiers=classifiers)
