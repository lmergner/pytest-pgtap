# -*- coding: utf-8 -*-
# Copyright (c) 2018 Luke Mergner and contributors

import pytest

pytest_plugins = ["pytester"]

HEADER = """
pgTap Connection: postgres://postgres@192.168.1.68/pytest-pgtap*
pgTap Schema: None*
"""

SQL_TESTS = """
-- Should return two successful tests
BEGIN;
    SELECT plan(2);
    SELECT fail('simple fail');
    SELECT pass('simple pass');
    SELECT * FROM finish();
ROLLBACK;
"""

PYTHON_TESTS = """
def test_pgtap_fixture(pgtap):
    assert pgtap(
        "select has_column('whatever.contacts', 'name', 'contacts should have a name');")
"""

INI = """
[pytest]
addopts = 
log_cli = True
log_level = DEBUG
"""


@pytest.fixture
def result(testdir, database):
    testdir.plugins.append("pytest_pgtap")
    testdir.makefile(".sql", test_sql_file=SQL_TESTS)
    testdir.makepyfile(test_pgtap_fixture=PYTHON_TESTS)
    testdir.makeini(INI.format(database))
    result = testdir.runpytest("-v", "--pgtap-uri", database)
    return result


def test_pytest_plugin_returncode(result):
    assert result.ret == 1


def test_pytest_plugin_stdout_has(result):
    expected = HEADER.splitlines()
    expected.extend(["plugins: * pgtap-*", "collecting ... collected 2 items*"])
    result.stdout.fnmatch_lines_random(expected)


def test_pytest_plugin_results(result):
    result.assert_outcomes(failed=1, passed=1)
