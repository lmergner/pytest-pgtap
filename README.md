NOTE:  This is non-functioning alpha software.

pytest-pgtap is `pytest_plugin` that allows pytest to discover, run, and
aggregate pgTap PostgreSQL tests.

v0.1.0-alpha

[![Build Status](https://travis-ci.org/lmergner/pytest-pgtap.svg?branch=master)](https://travis-ci.org/lmergner/pytest-pgtap)

## Requirements

- pytest test suite
- psql installed on the machine running pytest-pgtap
- PostgreSQL with pgTap installed somewhere

## Installation

```
$ pip install https://github.com/lmergner/pytest-pgtap
```

Optionally install the cli runner:

```
$ pip install https://github.com/lmergner/pytest-pgtap[cli]
```


## Usage

The cli:
```
$ pgtap --uri [DATABASE_URL] tests/
```

With pytest:
```
$ pytest --pgtap-uri [DATABASE_URL]
```

Using the experimental pytest fixture:

```

def test_with_a_fixture(pgtap):
    pgtap('SELECT pass('this test passes;')
```

The idea is that the plugin will calculate the plan and wrap the test in the
pgtap boilerplate before invoking psql.  With [SqlAlchemy][] it might even be possible
to access the functions by name, i.e.  `func.pass`.


## License

Copyright (c) Luke Mergner 2018.

Distributed under the terms of the [MIT][] license, pytest-pgtap is free and open source software.

[MIT]: https://github.com/pytest-dev/pytest/blob/master/LICENSE
[pytest-pgtap]: https://www.github.com/lmergner/pytest-pgtap
[pytest]: https://pytest.org/
[pgtap]: https://pgtap.org
[tappy]: http://tappy.readthedocs.io/en/latest/
[posgresql]: https://www.postgresql.org/
[sqlalchemy]: http://www.sqlalchemy.org/
[howto]: https://medium.com/engineering-on-the-incline/unit-testing-postgres-with-pgtap-af09ec42795