#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='pytest-pgtap',
    version='0.1.0-alpha',
    description='Pytest plugin for running pgTAP tests',
    long_description=open('README.md').read(),
    author='Luke Mergner',
    author_email='lmergner@gmail.com',
    url='https://github.com/lmergner/pytest-pgtap',

    packages=['pytest_pgtap'],
    install_requires=[
        'pytest>=3.6.3',
        'sqlparse',
    ],
    extras_require={
        'cli': ['click'],
    },
    tests_require=[
        'pytest-cov',
        'pytest-mock',
    ],
    setup_requires=[
        'pytest_runner',
    ],
    entry_points={
        # TODO: make the pytest plugin optional
        'pytest11': [
            'pgtap = pytest_pgtap.plugin',
        ],
        'console_scripts': [
            'pgtap = pytest_pgtap.cli:cli [cli]'
        ],
    },
    include_package_data=False,
    license='MIT license',
    # TODO: Add platform
    # platforms=["unix", "linux", "osx", "cygwin", "win32"],
    classifiers=[
        # TODO: update classifiers
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Framework :: Pytest',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        # 'Programming Language :: Python :: 2.7',
    ],
    keywords=[
        'postgresql', 'pgTAP', 'pytest', 'py.test'
    ]
)
