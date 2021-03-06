# -*- coding: utf-8 -*-
# Copyright (c) 2018 Luke Mergner and contributors
"""
A pytest plugin for running pgTAP tests.
"""

__version__ = "0.1.0-alpha"
__author__ = "Luke Mergner <lmergner@gmail.com>"

import logging

logging.getLogger("pytest-pgtap").addHandler(logging.NullHandler())
