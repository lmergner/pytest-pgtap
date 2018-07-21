"""
invoke tasks instead of a makefile
"""

import os
import sys
import time
from urllib.parse import urlparse

from invoke import task

db_name = 'pytest-pgtap'
docker_name = 'pytest-pgtap'
pg_ip = urlparse(os.environ.get('DOCKER_HOST', '0.0.0.0:2975')
                 ).netloc.split(':')[0]
pg_url = f'postgres://postgres@{pg_ip}:5432/{db_name}'


def db_is_running(c):

    result = c.run(
        'docker inspect %s --format="{{.State.Health.Status}}"' % docker_name, hide='both', warn=True)
    if result.stdout.strip() == "healthy":
        return True
    return False


@task
def info(c, psql=False, url=False):
    if psql:
        print(psql_prefix)
    elif url:
        print(pg_url)
    else:
        print("psql prompt: %s" % psql_prefix)
        print("pytest prompt: pytest --pgtap-uri %s" % pg_url)


@task
def stop(c):
    c.run(f'docker stop {docker_name}', warn=True)


@task
def run(c):
    """docker run pytest-pgtap"""
    print('Starting the container...')
    c.run(
        f'docker run --rm -d --name {docker_name} -p 5432:5432 lmergner/pgtap:latest', hide='both')

    print('Waiting for the database to start up...')
    while not db_is_running(c):
        time.sleep(15)

    print('Running setup.sql...')
    c.run(psql_prefix + ' -f tests/setup.sql', hide='both')


@task(stop, run)
def test(c, stop=True):
    """ Run the tests in a docker database """
    c.run('pytest --pgtap-uri %s' % pg_url)


@task
def clean(c):
    """ Remove all the crap """
    todo = '''
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache '''.splitlines()
    for cmd in todo:
        c.run(cmd)


@task
def lint(c):
    c.run('pylint pytest_pgtap')
    # TODO: add autopep8, which is installed by vscode


@task
def typing(c):
    c.run('mypy --ignore-missing-imports pytest_pgtap')
