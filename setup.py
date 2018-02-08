#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


with open('requirements.txt') as f:
    install_requires = f.read().split('\n')


setup(
    name='pytest-pgtap',
    version='0.0.1dev',
    description='Pytest plugin for running pgTAP tests',
    # long_description=open('README.txt').read(),
    author='Luke Mergner',
    author_email='lmergner@gmail.com',
    url='https://github.com/lmergner/pytest-pgtap',

    packages=['pytest_pgtap'],
    install_requires=install_requires,
    tests_require=[
        'pytest',
        'pytest-cov',
    ],
    setup_requires=[
        'pytest_runner',
    ],
    entry_points={
        'pytest11': [
            'pgtap = pytest_pgtap.plugin',
            ],
        'console_scripts': [
            ],
        },
    include_package_data=False,
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Framework :: Pytest',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords=[
        'postgresql', 'pgTAP', 'pytest', 'py.test'
    ]
)
