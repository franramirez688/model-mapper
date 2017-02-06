# -*- coding: utf-8 -*-

import os
from setuptools import setup

from modelmapper import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='modelmapper',
    version=__version__,
    author='Taric S.A.',
    author_email='desarrollo.madrid@taric.es',
    maintainer='Desarrollo Taric',
    maintainer_email='desarrollo.madrid@taric.es',
    long_description=read('README.md'),
    description='Gestor de conexiones entre estructuras de datos',
    packages=['modelmapper']
)
