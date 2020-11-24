# -*- coding: utf-8 -*-
# Copyright (c) 2018 Luke Mergner and contributors
"""
    pgTAP plugin for pytest
"""

import logging
import os

import pytest  # type: ignore

from .pgtap import Runner, match_file_name

logger = logging.getLogger("pytest-pgtap")


class TestError(Exception):
    """ Represent a pgTap test failure """

    pass


def pytest_addoption(parser):
    """ pytest hook:  add options to the pytest cli """
    group = parser.getgroup("pgtap", "pgtap test runner")
    group.addoption(
        "--pgtap-uri",
        help="database uri, defaults to DATABASE_URL env",
        default=os.environ.get("DATABASE_URL"),
    )
    group.addoption(
        "--pgtap-schema",
        default=None,
        help="Schema in which to find xUnit tests; " "Run xUnit tests using runtests()",
    )
    group.addoption(
        "--pgtap-pattern",
        default="test_*.sql",
        help="test file name search pattern; Defaults to test_*.sql",
    )


def pytest_report_header(config):
    """pytest hook: return a string to be displayed
                    as header info for terminal reporting.
    """
    return "\n".join(
        [
            "pgTap Connection: {0}".format(config.getoption("pgtap_uri")),
            "pgTap Schema: {0}".format(
                config.getoption("pgtap_schema", default="runtests() disabled")
            ),
        ]
    )


def pytest_collect_file(path: str, parent) -> pytest.Collector:
    """ pytest hook: collect files for testing """
    if match_file_name(
        os.path.basename(path), parent.config.getoption("pgtap_pattern")
    ):
        logger.debug("Matched %s", path)
        return SQLItem(name=path, parent=parent)


@pytest.fixture(scope="session", autouse=True)
def _install_pgtap_extension(request):
    """ create extension pgtap if not exists;

        run once before tests, but after pytest_configure hook
    """
    psql = Runner(request.config.option.pgtap_uri)
    logger.debug("Creating the pgtap extension before tests...")
    psql.run("CREATE EXTENSION IF NOT EXISTS pgtap;")
    yield


# def pytest_collection_modifyitems(session, config, items):
# """ pytest hook:  modify collected tests before execution """
# Catch flag to run in-database tests
# cf. http://pgtap.org/documentation.html#runtests
# schema = config.getoption('pgtap_schema')
# if schema:
#     logger.debug('Appending the runtests query to collector items')
#     items.append(SQLItem(
#         name='<pgTAP runtests(%s)>' % schema,
#         parent=session,
#         # TODO: write test or verify that ::name is correct
#         teststr='select * from runtests(\'%s\'::name)' % schema))


class SQLItem(pytest.Item, pytest.File):
    def __init__(
        self, name: str, parent  # the path of the test file  # a pytest.Item or similar
    ):
        super().__init__(name, parent)
        with open(name) as f:
            self.test = f.read()
        self.runner = Runner(parent.config.getoption("pgtap_uri"))

    def runtest(self):
        result: str = self.runner.run(self.test)
        logger.debug("plugin pytest.Item.runtest %s", result)
        if "not ok" in result:
            raise TestError(result)

    def reportinfo(self):
        return self.test, None, " ".join(["pgTap", self.name])

    def repr_failure(self, excinfo):
        """
        Unwrap mypy errors so we get a clean error message without the
        full exception repr.
        """
        if excinfo.errisinstance(TestError):
            return excinfo.value.args[0]
        return super().repr_failure(excinfo)


@pytest.fixture
def pgtap(request):
    """ Fixture for writing pgTap sql tests in pytest

    ..code: Python
        def test_db(pgtap):
            assert pgtap(
                "select has_column('whatever.contacts', 'name', 'contacts should have a name');"
            )

    Consult the pgtap documentation.
    """
    runner = Runner(request.config.getoption("pgtap_uri"))

    # TODO:  Should return True or False, not a string
    def executor(teststr):
        return runner.run_with_plan(teststr)

    yield executor
