# -*- coding: utf-8 -*-
# Copyright (c) 2018 Luke Mergner and contributors
""" Test the pgtap cli runner """

from functools import partial
import logging
from subprocess import CompletedProcess
import pytest
from click.testing import CliRunner
from pytest_pgtap.cli import cli, log_level_name

SQL_TESTS = """
-- Should return two successful tests
BEGIN;
    SELECT plan(2);
    SELECT fail('simple fail');
    SELECT pass('simple pass');
    SELECT * FROM finish();
ROLLBACK;
"""


@pytest.fixture
def runner(tmpdir, database):
    sub = tmpdir.mkdir('tests')
    sub.copy('tests/sql-tests', 'tests')
    return partial(CliRunner().invoke, cli, ['pgtap', '--uri', database, sub.dirpath])


@pytest.mark.parametrize(
    'levelname, num', [
        (logging.WARNING, 2),
        (logging.DEBUG, 10),
        (logging.CRITICAL, 0),
    ]
)
def test_log_level(levelname, num):
    assert log_level_name(int(num), lower_bound=0) == levelname


def test_cli_exit_code(runner, subprocess):
    result = runner()
    mock = subprocess()
    mock.called_wth
