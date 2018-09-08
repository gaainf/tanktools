#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Alexander Grechin
#
# Licensed under the BSD 3-Clause license.
# See LICENSE file in the project root for full license information.
#

"""Setup module"""

import re
from os.path import join, dirname
from setuptools import setup, find_packages
# import tanktools

with open(join(dirname(__file__), 'tanktools', '__init__.py'), 'r') as f:
    VERSION_INFO = re.match(r".*__version__ = '(.*?)'",
                            f.read(), re.S).group(1)

with open('README.rst') as f:
    LONG_README = f.read()

SETUP_REQUIRES = [
    "pytest-runner",
]

REQUIRES = [
    'python-dateutil>=2.5.0',
    'pandas>=0.23.4',
]

TEST_REQUIRES = [
    'pytest>=2.7',
    'pytest-cov>=2.6.0',
]

setup(
    name='tanktools',
    version=VERSION_INFO,
    packages=find_packages(exclude=('tests', 'docs')),
    description='Yandex-tank tools',
    long_description=LONG_README,
    keywords='yandextank yandex-tank statistics tools utilities',
    author='Alexander Grechin',
    author_email='infinum@mail.ru',
    download_url='https://github.com/gaainf/tanktools',
    url='',
    license='BSD-3-Clause',
    install_requires=REQUIRES,
    setup_requires=SETUP_REQUIRES,
    tests_require=TEST_REQUIRES,
    test_suite='tests',
    classifiers=[
        'Development Status :: 1 - Beta',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
)
