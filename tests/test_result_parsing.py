#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from tap.loader import Loader

plan_str = """
1..4
ok 1 - Input file opened
not ok 2 - First line of the input valid.
    More output from test 2. There can be
    arbitrary number of lines for any output
    so long as there is at least some kind
    of whitespace at beginning of line.
ok 3 - Read the rest of the file
#TAP meta information
not ok 4 - Summarized correctly # TODO: not written yet
"""
pgtap_str = """
BEGIN
Time: 2.257 ms
1..2
Time: 51.971 ms
not ok 1 - contacts should have a name
# Failed test 1: "contacts should have a name"
Time: 27.505 ms
ok 2 - simple pass
Time: 9.215 ms
# Looks like you failed 1 test of 2
Time: 9.162 ms
ROLLBACK
Time: 3.595 ms
"""
success_str = " ok 2 - simple pass "

failure_str = """
 not ok 1 - contacts should have a name        ↵
 # Failed test 1: "contacts should have a name"
"""


def test_result_success():
    l = Loader()
    result = l.load_suite_from_text('tests/test_plan_str.sql', plan_str)
