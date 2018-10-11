# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

from modelmapper import __version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='modelmapper',
    version=__version__,
    author='Francisco Ramirez de Anton',
    long_description=read('README.md'),
    description='Gestor de conexiones entre estructuras de datos',
    packages=find_packages(exclude=['tests', 'tests.*'])
)
