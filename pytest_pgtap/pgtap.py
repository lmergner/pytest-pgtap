# -*- coding: utf-8 -*-
# Copyright (c) 2018 Luke Mergner and contributors
"""
    core functionality for pgTap python implementation
"""

import abc
import fnmatch
import logging
import os
import shlex
import subprocess
from typing import Dict, Generator, List

import sqlparse

from .uri import make_url

logger = logging.getLogger("pytest-pgtap")


class PsqlError(Exception):
    """ psql reported an error or exited prematurely """

    pass


class Executor(abc.ABC):
    @abc.abstractmethod
    def run(self, test: str):
        """ Run a query against a database """
        pass


class Shell(Executor):
    @abc.abstractproperty
    def command(self) -> str:
        """ Return a string representation of a database shell command """
        pass

    @property
    def command_tokens(self) -> List[str]:
        """ Return a shlex.split list of the database command """
        return shlex.split(self.command)


class Psql(Shell):
    """ run pgTap test through psql """

    default_psql_command: str = """
        psql
        --no-psqlrc
        --no-align
        --quiet
        --pset pager=off
        --pset tuples_only=true
        --set ON_ERROR_STOP=1
    """

    default_psql_kwargs: Dict[str, bool] = dict(text=True, capture_output=True)

    def __init__(self, psql_uri: str = None):
        self.psql_opts = make_url(psql_uri)

    @property
    def command(self) -> str:
        """ Return the psql command """
        # Strip off the leading tabs
        cmd = " ".join(
            [line.strip() for line in self.default_psql_command.splitlines()]
        ).strip()
        cmd += " --dbname %s" % self.psql_opts
        return cmd

    def runtests(self, schema: str = None, pattern: str = None) -> str:
        """ run pgTap runtests()

        runs all the tests defined as functions in the
        database.

        Note: this function is not related to the pytest runtest hook in `pytest.Item`.
        """
        query = "SELECT * FROM runtests("
        if schema:
            query += "'%s'::name" % schema
        if schema and pattern:
            query += ", "
        if pattern:
            query += "'%s'" % pattern
        query += ");"
        return self.run(query)

    def run(self, test: str) -> str:
        """ run an test where the test is a string """
        logger.debug("Runner.run() input\n\n%s\n%s\n", test, self.command)
        try:
            result = subprocess.run(
                self.command_tokens, input=test, **self.default_psql_kwargs
            )
            result.check_returncode()

        except subprocess.CalledProcessError:
            logger.error("psql subprocess error: %s" % result.stderr)
            raise
        else:
            return result.stdout

    def run_with_plan(self, test: str) -> str:
        """ run an sql test and automatically generate the pgtap test scaffolding """
        # xxx: do we really need sqlparse, even if it lets us properly count one-line tests
        return self.run(wrap_plan(*sqlparse.split(test)))


Runner = Psql


def find_test_files(
    path: str, pattern: str = "test_*.sql"
) -> Generator[str, None, None]:
    """ Yield list of matching file paths """
    # TODO: use glob.glob?
    for root, _, files in os.walk(path):
        for fname in files:
            if match_file_name(fname, pattern):
                yield os.path.join(root, fname)


def match_file_name(
    fname: str,
    pattern: str,
    exclude: List[str] = [],
    default_exclude: List[str] = ["__*__", ".*"],
) -> bool:
    """ Return True if name matches the pattern using `fnmatch` """
    if exclude not in default_exclude:
        default_exclude.extend(exclude)
    logger.debug(f"Comparing {fname} to {pattern} excluding {default_exclude}")
    return fnmatch.fnmatch(fname, pattern) and not any(
        [fnmatch.fnmatch(fname, ex) for ex in default_exclude]
    )


def wrap_plan(*lines: str) -> str:
    """ Wrap in pgtap plan functions, assumes each line is a test """
    # You can't run a pgTap query without a plan unless it's a
    # runtests() call to db test functions

    return "\n".join(
        [
            "BEGIN;",
            "SELECT plan(%s);" % len(lines),
            *lines,
            "SELECT * FROM finish();",
            "ROLLBACK;",
        ]
    )
