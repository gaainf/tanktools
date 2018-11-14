#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Alexander Grechin
#
# Licensed under the BSD 3-Clause license.
# See LICENSE file in the project root for full license information.
#

"""Setup module"""

from setuptools import setup, find_packages
import re
from os.path import join, dirname

with open('README.rst') as f:
    long_readme = f.read()

setuptools_kwargs = {
    'install_requires': [
        'python-dateutil>=2.5.0',
        'pandas>=0.23.4',
        'flake8>=3.5.0',
        'pcaper>=1.0.2'
    ],
    'setup_requires': 'pytest-runner',
    'tests_require': [
        'pytest>=2.7',
        'pytest-cov>=2.6.0',
        'mock>=2.0.0'
    ],
    'entry_points': {
        'console_scripts': [
            'pcap2ammo=tanktools.pcap2ammo:main'
        ],
    },
}

PACKAGE_NAME = 'tanktools'
AUTHOR = 'Alexander Grechin'
AUTHOR_EMAIL = 'infinum@mail.ru'
LICENSE = 'BSD'
with open(join(dirname(__file__), PACKAGE_NAME, '_version.py'), 'r') as f:
    VERSION = re.match(r".*__version__ = '(.*?)'", f.read(), re.S).group(1)

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    packages=find_packages(exclude=('tests', 'docs')),
    description='Yandex-tank tools',
    long_description=long_readme,
    keywords='yandextank yandex-tank statistics tools utilities',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    download_url='https://github.com/gaainf/tanktools',
    url='https://github.com/gaainf/tanktools',
    license='BSD-3-Clause',
    test_suite='tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Utilities'
    ],
    **setuptools_kwargs
)
