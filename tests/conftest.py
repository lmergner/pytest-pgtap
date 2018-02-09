import os
import subprocess
import shlex
import logging
import pytest

logging.basicConfig(level=logging.DEBUG)
pytest_plugins = 'pytester'


@pytest.fixture(autouse=True, scope='session')
def createdb(request):
    dbname = request.config.getoption('pgtap_uri')
    try:
        subprocess.run(shlex.split('createdb ' + dbname), check=True)
        if os.path.exists('tests/setup.sql'):
            subprocess.run(shlex.split(
                'psql -d ' + dbname + ' -f tests/setup.sql'), check=True)
        yield
    except subprocess.CalledProcessError:
        # TODO: handle in pytestable way
        raise
    finally:
        subprocess.run(shlex.split('dropdb ' + dbname))
