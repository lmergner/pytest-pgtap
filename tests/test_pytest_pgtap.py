import pytest

pytest_plugins = ['pytester']

tmpconf = """
import os
import subprocess
import shlex
import logging
import pytest

pytest_plugins = ['pytest_pgtap']

@pytest.fixture(autouse=True, scope='session')
def resetdb():
    # dbname = session.config.getoption('pgtap_uri')
    dbname = 'pytest-pgtap'
    try:
        subprocess.run(shlex.split('dropdb --if-exists ' + dbname), check=True)
        subprocess.run(shlex.split('createdb ' + dbname), check=True)
        subprocess.run(shlex.split(
            'psql -d ' + dbname + ' -f tests/setup.sql'), check=True)
        yield
    except subprocess.CalledProcessError as e:
        # TODO: handle in pytestable way
        raise
    finally:
        subprocess.run(shlex.split('dropdb ' + dbname), check=True)
"""

tmpsetup = """
BEGIN;
CREATE EXTENSION IF NOT EXISTS pgtap;
CREATE SCHEMA IF NOT EXISTS whatever;
CREATE TABLE IF NOT EXISTS whatever.contact (
    id serial primary key,
    name varchar(40) NOT NULL,
    created_on date DEFAULT now()
);

CREATE OR REPLACE FUNCTION whatever.setup() RETURNS SETOF TEXT AS $$
    SELECT text('Setup...');
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION whatever.test_passing() RETURNS SETOF TEXT AS $$
    SELECT collect_tap(ARRAY[
        pass('simple pass'),
        pass('another simple pass')
    ]);
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION whatever.test_failing() RETURNS SETOF TEXT AS $$
    SELECT fail('simple fail');
$$ LANGUAGE SQL;


CREATE OR REPLACE FUNCTION whatever.teardown() RETURNS SETOF TEXT AS $$
    SELECT text('Teardown...');
$$ LANGUAGE SQL;

INSERT INTO whatever.contact (name) VALUES
    ('Luke'),
    ('Mike'),
    ('Sam'),
    ('George'),
    ('Jon'),
    ('Howard');
COMMIT;
"""

tmptest = """
BEGIN;
    SELECT plan(2);
    SELECT has_column('whatever.contact', 'name', 'contacts should have a name');
    SELECT pass('simple pass');
    SELECT * FROM finish();
ROLLBACK;
"""
test_string = "SELECT has_column('whatever.contact', 'name', 'contacts should have a name');"


@pytest.fixture
def scaffold(testdir):
    testdir.makeconftest(tmpconf)
    testdir.makefile('.sql', setup=tmpsetup, test_pgtap=tmptest)


def test_filter(scaffold):
    pass
