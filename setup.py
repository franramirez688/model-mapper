# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages


here = os.path.dirname(os.path.abspath(__file__))
README = open(os.path.join(here, 'README.md')).read()

from modelmapper import __version__


setup(
    name='modelmapper',
    version=__version__,
    author='Taric S.A.',
    author_email='desarrollo.madrid@taric.es',
    maintainer='Desarrollo Taric',
    maintainer_email='desarrollo.madrid@taric.es',
    long_description=README,
    description='Gestor de conexiones entre estructuras de datos',
    packages=find_packages()
)
