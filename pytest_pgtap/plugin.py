"""pgTAP plugin for pytest"""

import pytest
import os
import re
import logging
import warnings
# xxx: Catch annoying warning about psycopg2 wheels
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    import psycopg2

logger = logging.getLogger('pytest-pgtap')
logging.basicConfig(level=logging.DEBUG)
# logger.setLevel(logging.DEBUG)


class SQLFailure(Exception):
    """ Represent a Test Failure """
    pass


# TODO:  Write tests for runtests in public schema
# TODO:  Do we need a disable flag?
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


# TODO: write test for runtests
def pytest_collection_modifyitems(session, config, items):
    # Catch flag to run in-database tests
    # cf. http://pgtap.org/documentation.html#runtests
    schema = config.getoption('pgtap_schema')
    if schema:
        logger.debug('Appending the runtests query to collector items')
        items.append(SQLItem(
            name='<pgTAP runtests(%s)>' % schema,
            parent=session,
            teststr='select * from runtests(%s::name)' % schema))


def test_line(line, strip_plan=False):
    """ return false if the line is pgTap boilerplate """

    ignore_transaction_matches = [
        'BEGIN;',
        'ROLLBACK;',
        ]

    ignore_plan_matches = [
        'SELECT * FROM finish();',
        'SELECT plan',
        ]

    # All your indents are for naught
    line = line.strip()

    # what lines should we remove from the pgTap file?
    # Psycopg2 has it's own transaction scope
    # but we might also want to run tests without
    # the plan() or finish() calls
    ignores = ignore_transaction_matches
    if strip_plan:
        ignores.extend(ignore_plan_matches)

    # discard blank lines
    if not line:
        return False

    # filter by ignores
    # TODO: switch to regex?
    for prefix in ignores:
        if line.startswith(prefix):
            return False
    return True


# Regex borrowed from tappy
# https://raw.githubusercontent.com/python-tap/tappy/master/tap/parser.py
# ok and not ok share most of the same characteristics.
result_regex = re.compile(r"""
    ^[\s]*                     # Optional whitespace
    (?P<bool>(?:[\w]?) ok)           # Result
    [\s]+                      # Optional whitespace.
    (?P<number>\d*)            # Optional test number.
    [\s\-]+                    # Optional whitespace.
    (?P<description>[^#\(\+]*) # Optional description before #.
""", re.VERBOSE)
def parse_result_line(line):
    line = line.strip()
    print('LINE::: %s' % line)
    match = result_regex.match(line)
    if match:
        return match
    return None


def plan_wrapper(*lines):
    """ Wrap in pgtap plan functions, assumes each line is a test """
    # You can't run a pgTap query without a plan unless it's a
    # runtests() call to db test functions
    num = len(lines)
    return '\n'.join([
        f"SELECT plan({num});",
        *lines,
        "SELECT * from finish();",
        ])


class SQLItem(pytest.Item):
    """ """

    def __init__(self, name, parent, teststr, use_plan=False):
        super().__init__(name, parent)
        self.name = name
        self.teststr = teststr
        self.use_plan = use_plan

    def setup(self):
        self.uri = self.config.getoption('pgtap_uri')
        self.connection = psycopg2.connect(self.uri)

    def runtest(self):
        """ execute each pgtap stmt individually to capture output """

        # convert str to a list and filter out transaction stmts
        plan = [line for line in self.teststr.strip().splitlines() if test_line(line)]

        # sometimes we might need to wrap individual tests in plan / finish
        if self.use_plan:
            plan = plan_wrapper(plan)

        results = []
        for line in plan:
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(line)
                    for row in cursor:
                        logger.debug(row)
                        results.append(Result(row))
            except psycopg2.ProgrammingError as e:
                logger.error('Error parsing: %s %s', self.name, e)
                raise
        return results

    # def reportinfo(self):
    #     pass

    # TODO:  how do we report failure / success
    def repr_failure(self, excinfo):
        if excinfo.errisinstance(SQLFailure):
            return excinfo.value.args[0]
        return super().repr_failure(excinfo)


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


class Result(object):
    """ represent a Tap Result """

    # Regex borrowed from tappy
    # https://raw.githubusercontent.com/python-tap/tappy/master/tap/parser.py
    # ok and not ok share most of the same characteristics.
    result_regex = re.compile(r"""
        ^[\s]*                     # Optional whitespace
        (?P<bool>\w? ok)           # Result
        [\s]+                      # Optional whitespace.
        (?P<number>\d*)            # Optional test number.
        [\s\-]+                    # Optional whitespace.
        (?P<description>[^#\(\+]*) # Optional description before #.
    """, re.VERBOSE | re.MULTILINE)

    # \#?                         # Optional directive marker.
    # \s*                    # Optional whitespace.
    # (?P<directive>.*)      # Optional directive text.
    # success_regex = re.compile(r'^[\s*](?<!not\s)ok' + base_regex, re.VERBOSE | re.MULTILINE)
    # failure_regex = re.compile(r'^\s*not\s*ok' + base_regex, re.VERBOSE | re.MULTILINE)

    def __init__(self, result, ident=None):
        self.raw = result.strip()
        self.ident = ident  # who keeps track of test traceback, us or pytest?

        logger.debug('Parsing: %s', self.raw)

        # group_keys = ('bool', 'number', 'description')
        try:
            match = self.result_regex.search(self.raw)
            if match:
                _bool = match.groupdict().get('bool', None)
                if _bool and _bool.startwith('not'):
                    self.bool = False
                if _bool and _bool.startwith('ok'):
                    self.bool = True
                else:
                    logger.debug('Couldn\'t decide if result was true or false')
                self.number = int(match.groupdict().get('number', None))  # pytap reported test number
                self.description = match.groupdict().get('description', None)
                # self.directive = match.directive

        except AttributeError as e:
            logger.error('Expected a regex match object.')

    def __bool__(self):
        return self.bool or None
    __nonzero__ = __bool__


@pytest.fixture
def pgtap(request):
    """ Fixture for writing pgTap sql tests in pytest

    ..code:Python
        def test_db(pgtap):
            assert pgtap("select has_column('contacts', 'name', 'contacts should have a name');")

    Consult the pgtap documentation.
    """
    uri = request.config.getoption('pgtap_uri')
    connection = psycopg2.connect(uri)

    def executor(teststr, use_plan=True):
        results = []
        plan = plan_wrapper(teststr)

        for line in plan:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(line)
                    for row in cursor:
                        results.append(Result(row))
                return results
            except psycopg2.ProgrammingError as e:
                # TODO: handle error
                raise
    yield executor
