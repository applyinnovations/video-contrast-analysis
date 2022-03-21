# -*- coding: utf-8 -*-

from ast import parse
from os import path

from setuptools import setup, find_packages

if __name__ == '__main__':
    package_name = 'video_contrast_analysis'

    with open(path.join(package_name, '__init__.py')) as f:
        __author__, __version__ = map(
            lambda buf: next(map(lambda e: e.value.s, parse(buf).body)),
            filter(lambda line: line.startswith('__version__') or line.startswith('__author__'), f)
        )

    setup(
        name=package_name,
        description='Run video contrast analysis, outputting result to a subtitle file.',
        author=__author__,
        version=__version__,
        install_requires=[],
        #test_suite=package_name + '.tests',
        packages=find_packages(),
        package_dir={package_name: package_name}
    )
