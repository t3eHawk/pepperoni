"""Setup."""

import setuptools
import pepperoni


with open('README.md', 'r') as fh:
    long_description = fh.read()


install_requires = ['sqlalchemy>=1.3.1']


name = 'pepperoni'
author = pepperoni.__author__
email = pepperoni.__email__
version = pepperoni.__version__
description = 'Developer-friendly Python toolkit.'
license = pepperoni.__license__


setuptools.setup(
    name=name,
    version=version,
    author=author,
    author_email=email,
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    license=license,
    url='https://github.com/t3eHawk/pepperoni',
    install_requires=install_requires,
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
