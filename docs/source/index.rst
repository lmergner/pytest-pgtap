.. pytest-pgtap documentation master file, created by
   sphinx-quickstart on Sat Feb 10 09:56:01 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pytest-pgtap
============

Pytest-pgTap is a :lib:`pytest` plugin.

It is designed to be a replacement for the pgTap test runner `pg_prove`, which is a
`TAP https://testanything.org/` runner written in Perl.

Your should read the documentation for `pgTap http://pgtap.org/documentation.html`,
which describes the functions and strategies for testing `PostgreSQL https://www.postgresql.org/`
schemas, etc.

Why?

I wanted a to run tests against my alembic revisions and pgTap is a great tool, but I have
no idea how to install a CPAN package. Anyway, if you are testing against a Flask or Django
app (or whatever), it's easier to have a single test runner. Hence a plugin for pytest.

What?

Pytest-pgTap attempts to provide three entry points into the
pgTap test framework.

..code-block::SQL
    -- Start transaction and plan the tests.
    BEGIN;
    SELECT plan(1);

    -- Run the tests.
    SELECT pass( 'My test passed, w00t!' );

    -- Finish the tests and clean up.
    SELECT * FROM finish();
    ROLLBACK;

..note: Because we query through `psycopg2` instead of psql, the
        constructor will strip transaction directives out of the SQL file.




.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
