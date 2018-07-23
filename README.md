**pytest-pgtap is alpha software.**

pytest-pgtap is [pytest plugin][] that allows pytest to discover, run, and aggregate [pgTap][] [PostgreSQL][] tests as part of your pytest suite.

[![Build Status](https://travis-ci.org/lmergner/pytest-pgtap.svg?branch=master)](https://travis-ci.org/lmergner/pytest-pgtap)

## Rationale

Say you have a database migration plan using a tool like [Alembic][]. You should probably run some basic tests against your database to test those migrations. pgTap is a great tool for that. You could install and run those pgTap test using pytest_pgtap as part of your normal test ecosystem. At least that's the goal:  a purely python alternaltive to [pg_prove][].
## Requirements

- **Python 3.7** is the only tested version; some idiot wanted to learn about types
- [pytest][]
- psql
    Used internally to shell out using `subprocess.run`.
- [PostgreSQL][]
- [pgTap][]
    pytest-pgtap does not install or create the extension for pgTap. Consult their
    documentation for how to do that.

There is a [docker container](https://github.com/lmergner/docker-pgtap) that is used for testing, but you should know that it takes forever to boot up.

## Installation

pytest-pgtap is **not** on pypi so please install from the github repo.

```
$ pip install -U https://github.com/lmergner/pytest-pgtap
```

## Usage

With pytest:
```
$ pytest --pgtap-uri [DATABASE_URL] tests/
```

Note:  dropped the idea of a drop-in pg_prove pure python replacement.  While there may be value in such a utility, it seems possible to emulate using only pytest.

Using the **experimental** pytest fixture:

```
def test_with_a_fixture(pgtap):
    pgtap('SELECT pass('this test passes;')
```

The idea is that the plugin will calculate the plan and wrap the test in the pgtap boilerplate before invoking psql.  With [SqlAlchemy][] it might even be possible to access the functions by name, i.e.  `func.pass`. In other words, the goal is to introduce a pytest-friendly set of symantics for expressing a pgTap test suite.  The library isn't there yet, so create an issue.


## License

Copyright (c) Luke Mergner 2018.

Distributed under the terms of the [MIT][] license, pytest-pgtap is free and open source software.

[MIT]: https://github.com/pytest-dev/pytest/blob/master/LICENSE
[pytest-pgtap]: https://www.github.com/lmergner/pytest-pgtap
[pytest]: https://pytest.org/
[pgtap]: https://pgtap.org
[pg_prove]: https://pgtap.org/pg_prove.html
[tappy]: http://tappy.readthedocs.io/en/latest/
[postgresql]: https://www.postgresql.org/
[sqlalchemy]: http://www.sqlalchemy.org/
[howto]: https://medium.com/engineering-on-the-incline/unit-testing-postgres-with-pgtap-af09ec42795
[Alembic]: http://alembic.zzzcomputing.com/en/latest/
[pytest plugin]: https://plugincompat.herokuapp.com/
