**pytest-pgtap is alpha software.**

pytest-pgtap is [pytest plugin][] that allows pytest to discover, run, and
aggregate [pgTap][] [PostgreSQL][] tests as part of your pytest suite.

## Installation

pytest-pgtap is **not** on pypi so please install from the github repo.

```
$ pip install -U git+https://github.com/lmergner/pytest-pgtap.git
```

## Rationale

Say you have a database migration plan using a tool like [Alembic][]. You should probably
run some basic tests against your database to test those migrations. pgTap is a great tool for
that. You could install and run those pgTap test using pytest_pgtap as part of your normal test
ecosystem. At least that's the goal: a purely python alternaltive to [pg_prove][].

## Requirements

- **Python 3.7** is the only tested version; some idiot wanted to learn about types
- [pytest][]
- psql
  Used internally to shell out using `subprocess.run`.
- [PostgreSQL][]
- [pgTap][]
  pytest-pgtap does not install or create the extension for pgTap. Consult their
  documentation for how to do that.

  If you clone this repo, you can run:
  `bash install-pgtap.sh`
  But it may be osx only!

There is a [docker container](https://github.com/lmergner/docker-pgtap) that is used
for testing, but you should know that it takes forever to boot up.

## Usage

With pytest:

```
$ pytest --pgtap-uri [DATABASE_URL] tests/
```

Note: dropped the idea of a drop-in pg_prove pure python replacement. While there may be
value in such a utility, it seems possible to emulate using only pytest.

Using the **experimental** pytest fixture:

```
def test_with_a_fixture(pgtap):
    pgtap('SELECT pass('this test passes;')
```

The idea is that the plugin will calculate the plan and wrap the test in the pgtap
boilerplate before invoking psql. With [SqlAlchemy][] it might even be possible
to access the functions by name, i.e. `func.pass`. In other words, the goal is to
introduce a pytest-friendly set of symantics for expressing a pgTap test suite. The
library isn't there yet, so create an issue.

If you are testing for complex types that need quotes, you may need to escape in the sql file.

```
BEGIN;
    SELECT plan(1);
    SELECT col_default_is('tweet', 'created', E'timezone(\'utc\'::text, CURRENT_TIMESTAMP)');
    SELECT * from finish();
ROLLBACK;
```

[mit]: https://github.com/pytest-dev/pytest/blob/master/LICENSE
[pytest-pgtap]: https://www.github.com/lmergner/pytest-pgtap
[pytest]: https://pytest.org/
[pgtap]: https://pgtap.org
[pg_prove]: https://pgtap.org/pg_prove.html
[tappy]: http://tappy.readthedocs.io/en/latest/
[postgresql]: https://www.postgresql.org/
[sqlalchemy]: http://www.sqlalchemy.org/
[howto]: https://medium.com/engineering-on-the-incline/unit-testing-postgres-with-pgtap-af09ec42795
[alembic]: http://alembic.zzzcomputing.com/en/latest/
[pytest plugin]: https://plugincompat.herokuapp.com/
