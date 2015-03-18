#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of census2dbf.
# https://github.com/fitnr/census2dbf

# Licensed under the GPLv3 license:
# http://www.opensource.org/licenses/GPLv3-license
# Copyright (c) 2015, Neil Freeman <contact@fakeisthenewreal.org>

from setuptools import setup
from census2dbf import __version__

setup(
    name='census2dbf',

    version=__version__,

    description='Convert US Census CSV files into DBFs',

    long_description=open('readme.rst', 'r').read(),

    keywords='GIS DBF Census',

    author='Neil Freeman',

    author_email='contact@fakeisthenewreal.org',

    url='https://github.com/fitnr/census2dbf',

    license='GPLv3',

    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPLv3 License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
    ],

    packages=['census2dbf'],

    include_package_data=False,

    zip_safe=True,

    install_requires=[
    ],

    use_2to3=True,

    entry_points={
        'console_scripts': [
            'census2dbf=census2dbf.cli:main',
        ],
    },
)
