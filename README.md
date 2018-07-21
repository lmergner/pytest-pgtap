pytest-pgtap is `pytest_plugin`_ that allows pytest to discover, run, and
aggregate pgTap PostgreSQL tests.

Requirements
------------

- pytest test suite
- psql installed on the machine running pytest-pgtap
- PostgreSQL with pgTap installed somewhere

Installation
------------

    pip install pytest-pgtap

Optionally install the cli runner:

    pip install pytest-pgtap[cli]




License
-------

Copyright Luke Mergner 2018.

Distributed under the terms of the `MIT`_ license, pytest is free and open source software.

.. _`MIT`: https://github.com/pytest-dev/pytest/blob/master/LICENSE
.. _`pytest-pgtap`: https://www.github.com/lmergner/pytest-pgtap
.. _pytest`: https://pytest.org/
.. _pgtap`: https://pgtap.org
.. _tappy`: http://tappy.readthedocs.io/en/latest/
.. _posgresql`: https://www.postgresql.org/