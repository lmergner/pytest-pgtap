-- Copyright (c) 2018 Luke Mergner and contributors
BEGIN;
CREATE EXTENSION IF NOT EXISTS pgtap;
CREATE SCHEMA IF NOT EXISTS whatever;
CREATE TABLE IF NOT EXISTS whatever.contact (
    id serial primary key,
    name varchar(40) NOT NULL,
    created_on date DEFAULT now()
);

-- A Setup Fixture for pgTap runtests();
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

-- A TearDown Fixture for pgTap runtests();
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