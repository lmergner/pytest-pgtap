# Copyright (c) 2018 Luke Mergner and contributors
""" Test the pgtap cli runner """

from functools import partial
import logging
from subprocess import CompletedProcess
import pytest
from click.testing import CliRunner
from pytest_pgtap.cli import cli, log_level_name


@pytest.fixture
def runner(tmpdir, database):
    sub = tmpdir.mkdir('tests')
    tf = sub.join('test_passing.sql')
    tf.write('passing')
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
    # TODO: What am i testing here?
