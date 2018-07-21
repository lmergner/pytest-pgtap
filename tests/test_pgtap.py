# Copyright (c) 2018 Luke Mergner and contributors

from subprocess import CompletedProcess
import sys
import pytest  # type: ignore
import unittest
from pytest_pgtap import pgtap


def assert_args_in(m, *mock_args, **mock_kwargs):
    """ Test for arg or kwarg in mock.call_args 

    ...instead of having to supply a complete list of args, kwargs
    to mock.assert_called_with()
    """
    __tracebackhide__ = True
    args, kwargs = m.call_args

    for arg in mock_args:
        if not arg in args:
            pytest.fail('Expected arg {} in mock.call_args {}'.format(
                arg, args
            ))
    for key in mock_kwargs:
        if not key in kwargs:
            pytest.fail('Expected kwarg {} in mock.call_args {}'.format(
                key, kwargs
            ))
        elif mock_kwargs[key] != kwargs[key]:
            pytest.fail('Expected kw value {} in mock.call_args to match {}'.format(
                mock_kwargs[key], kwargs[key]
            ))


@pytest.mark.parametrize(
    "args, result", [(
        {'host': None, 'username': None, 'database': None, 'port': 5432},
        ['psql', '--no-psqlrc', '--no-align', '--quiet', '--pset', 'pager=off',
            '--pset', 'tuples_only=true', '--set', 'ON_ERROR_STOP=1', '--dbname', 'postgres://:5432']
    ), (
        {'host': 'localhost', 'username': 'lmergner',
            'database': 'lmergner', 'port': 5432},
        ['psql', '--no-psqlrc', '--no-align', '--quiet', '--pset', 'pager=off', '--pset', 'tuples_only=true', '--set',
            'ON_ERROR_STOP=1', '--dbname', 'postgres://lmergner@localhost:5432/lmergner']

    )]
)
def test_Runner_args(args, result):
    """ Runner should build psql cmd without any empty flags """
    runner = pgtap.Runner(args)
    assert runner.psql_command_tokens == result


def test_Runner_query(database):
    query = """
    BEGIN;
        SELECT plan(1);
        SELECT pass('simple pass');
        SELECT * FROM finish();
    ROLLBACK;
    """
    expected = """
        1..1
        ok 1 - simple pass
    """
    # xxx: using .split() only checks that the tokens returned
    #      are the same, not that they whitespace and newlines
    #      match
    runner = pgtap.Runner(database)
    result = runner.run(query)
    assert result.split() == expected.split()


def test_Runner_runtests(database):
    expected = """
    # Subtest: whatever.test_failing()
    Setup...
    not ok 1 - simple fail
    # Failed test 1: "simple fail"
    Teardown...
    1..1
    # Looks like you failed 1 tests of 1
not ok 1 - whatever.test_failing
# Failed test 1: "whatever.test_failing"
    # Subtest: whatever.test_passing()
    Setup...
    ok 1 - simple pass
    ok 2 - another simple pass
    Teardown...
    1..2
ok 2 - whatever.test_passing
1..2
# Looks like you failed 1 test of 2
""".strip('\n')
    runner = pgtap.Runner(database)
    # 'whatever' is the schema defined in tests/setup.sql
    result = runner.runtests('whatever')
    assert result.splitlines() == expected.splitlines()


def test_Loader():
    tap_output = """
1..2
not ok 1 - contacts should have a name
# Failed test 1: "contacts should have a name"
ok 2 - simple pass
# Looks like you failed 1 test of 2
""".strip('\n')
    expected = """
F.
======================================================================
FAIL: <file=stream>
- contacts should have a name
----------------------------------------------------------------------

----------------------------------------------------------------------
Ran 2 tests in 0.000s

FAILED (failures=1)
""".strip('\n')

    suite = pgtap.Loader().load_suite_from_text('unittests', tap_output)
    assert len(suite._tests) == 2
    runner = unittest.TextTestRunner(verbosity=1, stream=sys.stderr)
    result = runner.run(suite)
    assert result.wasSuccessful() == False
    # TODO: test is incomplete... how do we test the unittest test suite?


@pytest.mark.parametrize(
    "schema, pattern, expected", [
        (None, None, 'SELECT * FROM runtests();'),
        ('whatever', None, 'SELECT * FROM runtests(\'whatever\'::name);'),
        (None, '^test', 'SELECT * FROM runtests(\'^test\');'),
        ('whatever', '^test', 'SELECT * FROM runtests(\'whatever\'::name, \'^test\');'),
    ])
def test_runtests_query_construction(subprocess, schema, pattern, expected):
    """ Runner.runtests should handle schema and pattern args """
    mock = subprocess()
    result = pgtap.Runner().runtests(schema=schema, pattern=pattern)
    assert_args_in(mock, input=expected)


@pytest.mark.parametrize(
    "query, expected", [(
        "SELECT pass('simple pass');", """
BEGIN;
SELECT plan(1);
SELECT pass('simple pass');
SELECT * FROM finish();
ROLLBACK;
""".strip()
    )]
)
def test_wrap_plan(query, expected):
    """ plan_wrap should return a list of strings that create a pgTap test case"""
    assert pgtap.wrap_plan(query) == expected


@pytest.mark.parametrize(
    'folder, filelist, expected', [
        ('.', ['test_file.sql', 'not-test.txt'], ['./test_file.sql']),
        ('tests/',  # folder
            ['test_file.sql', 'not-test.txt'],  # filelist
            ['tests/test_file.sql']  # expected
         )
    ]
)
def test_load_files(mocker, folder, filelist, expected):
    """ files from a tmpdir should be loaded by name """
    mock = mocker.patch('os.walk')
    mock.return_value = [
        (folder, [], filelist)
    ]
    assert list(pgtap.find_test_files(folder)) == expected


def test_Runner_run_with_plan(subprocess):
    test = 'SELECT pass(\'simple pass\');'
    expected = """
BEGIN;
SELECT plan(1);
SELECT pass('simple pass');
SELECT * FROM finish();
ROLLBACK;
""".strip()
    mock = subprocess()
    runner = pgtap.Runner()
    runner.run_with_plan(test)
    assert_args_in(mock, input=expected)
