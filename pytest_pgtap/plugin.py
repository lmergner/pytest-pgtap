# Copyright (c) 2018 Luke Mergner and contributors
"""
    pgTAP plugin for pytest
"""

import pytest  # type: ignore
import os
import logging

from .pgtap import match_file_name, pgTapError, Runner

logger = logging.getLogger('pytest-pgtap')


# TODO:  Write tests for runtests in public schema


def pytest_addoption(parser):
    group = parser.getgroup('pgtap', 'pgtap test runner')
    group.addoption('--pgtap-uri', help='database uri')
    group.addoption(
        '--pgtap-schema', default=None,
        help='Schema in which to find xUnit tests; '
             'Run xUnit tests using runtests()')
    group.addoption(
        '--pgtap-pattern', default='test_*.sql',
        help='test file name search pattern; Defaults to test_*.sql')


def pytest_report_header(config):
    '''
    return a string to be displayed as header info for terminal reporting.
    '''
    return '\n'.join([
        'pgTap Connection: {0}'.format(config.getoption('pgtap_uri')),
        'pgTap Schema: {0}'.format(config.getoption(
            'pgtap_schema', default='runtests() disabled'))
    ])


def pytest_collect_file(path, parent):
    if match_file_name(path, parent.config.getoption('pgtap_pattern')):
        logger.debug('Matched %s', path)
        return SQLFile(fspath=path, parent=parent)


def pytest_collection_modifyitems(session, config, items):
    # Catch flag to run in-database tests
    # cf. http://pgtap.org/documentation.html#runtests
    schema = config.getoption('pgtap_schema')
    # if schema:
    #     logger.debug('Appending the runtests query to collector items')
    #     items.append(SQLItem(
    #         name='<pgTAP runtests(%s)>' % schema,
    #         parent=session,
    #         # TODO: write test or verify that ::name is correct
    #         teststr='select * from runtests(\'%s\'::name)' % schema))


class SQLItem(pytest.Item):

    def __init__(self, name, parent, teststr):
        super().__init__(name, parent)
        # self.filename = filename

    def runtest(self):
        raise pgTapError

    def reportinfo(self):
        return ""

    def repr_failure(self, excinfo):
        """
        Unwrap mypy errors so we get a clean error message without the
        full exception repr.
        """
        if excinfo.errisinstance(pgTapError):
            return excinfo.value.args[0]
        return super().repr_failure(excinfo)


@pytest.fixture
def pgtap(request):
    """ Fixture for writing pgTap sql tests in pytest

    ..code: Python
        def test_db(pgtap):
            assert pgtap(
                "select has_column('contacts', 'name', 'contacts should have a name');")

    Consult the pgtap documentation.
    """
    runner = Runner(request.config.getoption('pgtap_uri'))

    def executor(teststr):
        return runner.run(teststr)
    yield executor
