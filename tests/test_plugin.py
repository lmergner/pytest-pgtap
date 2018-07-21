# Copyright (c) 2018 Luke Mergner and contributors

import pytest

# xxx: are we actually using this?
# xxx: Can we declare this here instead of conftest.py?
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
        "select has_column('contacts', 'name', 'contacts should have a name');")
"""

INI = """
[pytest]
addopts = --pgtap-uri {0}
"""


@pytest.fixture
def sql(testdir, database):
    testdir.plugins.append('pgtap')
    testdir.makeini(INI.format(database))
    return testdir


@pytest.mark.xfail
def test_sql_test(sql):
    sql.makefile('.sql', test_sql_file=SQL_TESTS)
    result = sql.runpytest()
    result.assert_outcomes(failed=1)


@pytest.mark.xfail
def test_python_fixture(sql):
    sql.makepyfile(test_pgtap_fixture=PYTHON_TESTS)
    result = sql.runpytest()
    result.assert_outcomes(passed=1)
