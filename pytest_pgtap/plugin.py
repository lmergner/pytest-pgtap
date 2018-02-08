"""pgTAP plugin for pytest."""

import pytest
import argparse
import psycopg2


class PGException(Exception):
    pass


def pytest_addoption(parser):
    group = parser.getgroup('pgtap', 'pgtap test runner')
    group.addoption(
            '--pgtap', action='append', default=[],
            help='run pgtap tests with pytest')

    # TODO: only needed if we shell out instead of using psycopg2
    group.addoption(
            '--pgtap-psql', help='Location of the psql client')
    group.addoption(
            '--pgtap-dbname',
            help='Database to which to connect')
    group.addoption(
            '--pgtap-host', default='localhost',
            help='Host to which to connect')
    group.addoption(
            '--pgtap-port', default='5432',
            help='Port to which to connect')
    group.addoption(
            '--pgtap-user', help='User with which to connect')
    group.addoption(
            '--pgtap-runtests', action='store_true', default=False,
            help='Run xUnit test using runtests()')
    group.addoption(
            '--pgtap-schema', help='Schema in which to find xUnit tests')
    group.addoption(
            '--pgtap-match', help='Regular expression to find xUnit tests')
    group.addoption(
            '--pgtap-ext', default='.pg',
            help='Set the extension for tests (default .pg)')
    group.addoption(
            '--pgtap-uri', help='database uri')



class PgPlugin(object):
    pass
