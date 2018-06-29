#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from pytest_pgtap.plugin import Result

success_str = " ok 2 - simple pass "
failure_str = """
 not ok 1 - contacts should have a name        ↵
 # Failed test 1: "contacts should have a name"
"""

def test_result_success():
    result = Result(success_str)
    assert result
    assert result.number == 1
    assert result.description == 'contacts should have a name'
    assert result.directive == None
