# Copyright (c) 2018 Luke Mergner and contributors

import pytest

pytest_plugins = ['pytester']

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
addopts = -p no:mock -p no:cov
log_cli = True
log_level = DEBUG
"""

HEADER = """
pgTap Connection: postgres://postgres@192.168.1.68/pytest-pgtap*
pgTap Schema: None*
"""


def test_isolated_filesystem(testdir, database):
    testdir.plugins.append('pytest_pgtap')
    testdir.makefile('.sql', test_sql_file=SQL_TESTS)
    testdir.makepyfile(test_pgtap_fixture=PYTHON_TESTS)
    testdir.makeini(INI.format(database))
    result = testdir.runpytest('-v', '--pgtap-uri', database)
    print(result.stdout.str())
    assert result.ret == 1
    result.stdout.fnmatch_lines_random(HEADER)
    result.stdout.fnmatch_lines_random([
        'plugins: pgtap-*',
        'collecting ... collected 2 items*'
    ])

    result.assert_outcomes(failed=1, passed=1)
