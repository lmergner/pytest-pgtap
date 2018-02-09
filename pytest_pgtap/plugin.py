"""pgTAP plugin for pytest."""

import os.path
import subprocess
import shlex
from contextlib import AbstractContextManager
import psycopg2
import pytest
import logging

logger = logging.getLogger('pytest-pgtap')


class SQLFailure(Exception):
    pass


def pytest_addoption(parser):
    group = parser.getgroup('pgtap', 'pgtap test runner')
    group.addoption(
            '--pgtap-psql', help='Location of the psql client')
    group.addoption(
            '--pgtap-uri', default='postgres://', help='Database to which to connect')
    group.addoption(
            '--pgtap-runtests', action='store_true', default=False,
            help='Run xUnit test using runtests()')
    group.addoption(
            '--pgtap-schema', help='Schema in which to find xUnit tests')
    group.addoption(
            '--pgtap-match', help='Regular expression to find xUnit tests')
    group.addoption(
            '--pgtap-ext', default='.sql',
            help='Set the extension for tests (default .sql)')
    group.addoption(
            '--pgtap-dumpfile', help='load a database from a backup')


def _is_test(line):
    """ Remove transaction lines from files """
    # TODO: move to regex?
    ignore_line_prefixes = [
        'BEGIN;',
        'ROLLBACK;',
        'SELECT * FROM finish();',
        'SELECT plan',
        ]
    for prefix in ignore_line_prefixes:
        if line.strip().startswith(prefix):
            return False
    return True


class SQLItem(pytest.Item):

    prelude = [
        'SELECT plan({plan});',
    ]
    tests = []
    epilogue = [
        'SELECT * from finish();',
    ]

    def __init__(self, lineno, filename, ident, teststr, *args, **kwargs):
        super().__init__(name=ident, *args, **kwargs)
        self.lineno = lineno
        self.fname = filename
        self.ident = ':'.join([os.path.basename(filename), str(lineno)])
        self.tests.append(teststr)

    def add_test(self, test):
        self.tests.append(test)

    def runtest(self):
        parts = []
        parts.extend(self.prelude)
        parts.extend(self.tests)
        parts.extend(self.epilogue)
        test = '\n'.join(parts).format(plan=1)
        logger.debug(test)

        try:
            with Session(self.config.getoption('pgtap_uri')) as sess:
                sess(test)

        except psycopg2.ProgrammingError as e:
            logger.error('Error parsing: %s:%s --> %s', self.fname, self.lineno, e)
            raise


class SQLFile(pytest.File):

    def collect(self):
        """ read the test file
        """
        basename = os.path.basename(self.fspath)
        with open(self.fspath) as test:
            lines = test.readlines()

        file_map = []
        for idx, line in enumerate(lines):
            line = line.strip()

            # discard blank lines
            if not line:
                continue

            # discard transaction lines
            if not _is_test(line):
                continue

            logger.debug(line)
            file_map.append(SQLItem(
                parent=self,
                lineno=idx + 1,
                filename=self.fspath,
                ident=':'.join([basename, str(idx + 1)]),
                teststr=line))

        return file_map


def pytest_collect_file(parent, path):
    if path.ext == parent.config.getoption('pgtap_ext')\
            and path.basename.startswith('test'):
        return SQLFile(path, parent)


class Session(AbstractContextManager):
    use_psql = False
    connection = None

    def __init__(self, uri):
        self.uri = uri

    def __enter__(self):
        self.connection = psycopg2.connect(self.uri)
        return self.connection.cursor().execute

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.rollback()
        self.connection.close()


class Shell(object):

    cmd = [
        'psql -X -d {uri}'
    ]
    result = None

    def __init__(self, uri, cmds=[]):
        self.uri = uri
        for cmd in cmds:
            self.build_cmd(cmd)

    def from_file(self, fname):
        if not os.path.isfile(fname):
            raise Exception('File must exist')
        self.build_cmd(f'-f {fname}')
        return self.run()

    def build_cmd(self, line):
        self.cmd.append(line)

    def run(self):
        _cmd = ' '.join(self.cmd).format(uri=self.uri)
        logger.debug(_cmd)
        result = subprocess.run(shlex.split(_cmd), stdout=subprocess.PIPE)
        self.result = result
        return result.stdout.decode('utf-8')
