"""pgTAP plugin for pytest.

..code-block::SQL
    -- Start transaction and plan the tests.
    BEGIN;
    SELECT plan(1);

    -- Run the tests.
    SELECT pass( 'My test passed, w00t!' );

    -- Finish the tests and clean up.
    SELECT * FROM finish();
    ROLLBACK;


http://pgtap.org/documentation.html
"""

import pytest
# from _pytest.fixtures import FixtureRequest
import os
import re
import logging
import warnings
# xxx: Catch annoying warning about wheels
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    import psycopg2

logger = logging.getLogger('pytest-pgtap')
logger.setLevel(logging.DEBUG)


class SQLFailure(Exception):
    """ Represent a Test Failure

    :param match: :class:`re.Match`
    """
    ident = None
    filename = None
    lineno = None
    description = None
    directive = None

    def __init__(self, match=None):
        # number, description, directive
        self.match = match
        if match:
            pass

    def __repr__(self):
        return str(self.match.groupdict())


def pytest_addoption(parser):
    group = parser.getgroup('pgtap', 'pgtap test runner')
    group.addoption(
            '--pgtap-uri', help='Database to which to connect')
    group.addoption(
            '--pgtap-schema', default=None,
            help='Schema in which to find xUnit tests,' +
                 'Run xUnit tests using runtests()')
    group.addoption(
            '--pgtap-ext', default='.sql',
            help='Set the extension for tests (default .sql)')


def pytest_collect_file(path, parent):
    ext = parent.config.getoption('pgtap_ext')
    if path.ext == ext and path.basename.startswith('test'):
        logger.debug('Matched %s', path)
        return SQLFile(fspath=path, parent=parent)


def pytest_collection_modifyitems(session, config, items):
    # Catch flag to run in-database tests
    schema = config.getoption('pgtap_schema')
    if schema:
        logger.debug('Appending the runtests query to collector items')
        items.append(SQLItem(
            name='<pgTAP runtests(%s)>' % schema,
            parent=session,
            teststr='select * from runtests(%s::name)' % schema))


class SQLItem(pytest.Item):
    """ Run one pgTap test file """

    ignore_transaction_matches = [
        'BEGIN;',
        'ROLLBACK;',
        ]

    ignore_plan_matches = [
        'SELECT * FROM finish();',
        'SELECT plan',
        ]

    # Regex borrowed from tappy
    # https://raw.githubusercontent.com/python-tap/tappy/master/tap/parser.py
    # ok and not ok share most of the same characteristics.
    regex_base = r"""
        \s*                    # Optional whitespace.
        (?P<number>\d*)        # Optional test number.
        \s*                    # Optional whitespace.
        (?P<description>[^#]*) # Optional description before #.
        \#?                    # Optional directive marker.
        \s*                    # Optional whitespace.
        (?P<directive>.*)      # Optional directive text.
    """
    success = re.compile(r'^ok' + regex_base, re.VERBOSE)
    failure = re.compile(r'^not\ ok' + regex_base, re.VERBOSE)
    uri = None

    def __init__(self, name, parent=None, teststr=None, use_plan=False):
        super(SQLItem, self).__init__(name, parent)
        self.name = name
        self.teststr = teststr
        self.use_plan = use_plan
        # xxx Hack to force conftest fixtures to load before running file tests
        #     Otherwise, database setup might not happen
        # self.fixture_request = None

    def setup(self):
        uri = self.config.getoption('pgtap_uri')
        self.connection = psycopg2.connect(uri)

        # xxx Hack to force conftest fixtures to load before running file tests
        #     Otherwise, database setup might not happen
        # self.fixture_request = _setup_fixtures(self)
        # globs = dict(getfixture=self.fixture_request.getfixturevalue)
        # for name, value in self.fixture_request.getfixturevalue('doctest_namespace').items():
        #     globs[name] = value
        # self.teststr.globs.update(globs)

    def test_line(self, line, strip_plan=False):
        """ return false if the line is pgTap boilerplate """
        line = line.strip()
        # what lines should we remove from the pgTap file?
        # Psycopg2 has it's own transaction scope
        # but we might also want to run tests without
        # the plan() or finish() calls
        ignores = self.ignore_transaction_matches
        if strip_plan:
            ignores.extend(self.ignore_plan_matches)

        # discard blank lines
        if not line:
            return False

        # filter by ignores
        # TODO: move to regex?
        for prefix in ignores:
            if line.startswith(prefix):
                return False
        return True

    def _plan_wrapper(self, *lines):
        """ Wrap in pgtap plan functions, assumes each line is a test """
        num = len(lines)
        return '\n'.join([
            f"SELECT plan({num});",
            *lines,
            "SELECT * from finish();",
            ])

    def runtest(self):
        """ execute each pgtap stmt individually to capture output """

        # xxx Hack to force conftest fixtures to load before running file tests
        #     Otherwise, database setup might not happen
        # fixture_request = _setup_fixtures(self)

        # convert str to a list and filter
        plan = [line for line in self.teststr.strip().splitlines() if self.test_line(line)]

        # sometimes we might need to wrap individual tests in plan / finish
        if self.use_plan:
            plan = self._plan_wrapper(plan)

        failures = []
        for line in plan:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(line)
                    for row in cursor:
                        logger.debug(row[0])
                        match = self.failure.match(row[0])
                        if match:
                            failures.append(SQLFailure(match))
            except psycopg2.ProgrammingError as e:
                logger.error('Error parsing: %s %s', self.name, e)
                raise

    # TODO:  how do we report failure / success
    def repr_failure(self, excinfo):
        if excinfo.errisinstance(SQLFailure):
            return excinfo.value.args[0]
        return super().repr_failure(excinfo)

    # def reportinfo(self):
    #     pass


class SQLFile(pytest.File):
    """ pytest subclass

    Reads a test file and creates individual test items from
    pgTap files. Assumes each file is a single test, since
    there are no setup or teardown hooks.
    """
    def collect(self):
        name = os.path.basename(self.fspath)
        with open(self.fspath) as tf:
            yield SQLItem(name, parent=self, teststr=tf.read())


# xxx Hack to force conftest fixtures to load before running file tests
#     Otherwise, database setup might not happen
# def _setup_fixtures(item):
#     """
#     Used by DoctestTextfile and DoctestModule to setup fixture information.

#     https://github.com/pytest-dev/pytest/pull/836/files
#     """
#     def func():
#         pass

#     item.funcargs = {}
#     fm = item.session._fixturemanager
#     item._fixtureinfo = fm.getfixtureinfo(node=item, func=func,
#                                                   cls=None, funcargs=False)
#     fixture_request = FixtureRequest(item)
#     fixture_request._fillfixtures()
#     return fixture_request

# @pytest.fixture(scope='session')
# def pgtap_namespace():
#     return dict()
