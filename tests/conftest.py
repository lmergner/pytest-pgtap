# -*- coding: utf-8 -*-
# Copyright (c) 2018 Luke Mergner and contributors

import os
import shlex
from subprocess import CompletedProcess, run
import sys
import time
from urllib.parse import urlparse

# import docker
import pytest


def db_is_running(container: str) -> bool:
    """ Return True if the database is ready to accept connections """
    cmd = 'docker inspect %s --format="{{.State.Health.Status}}"' % container
    result = run(shlex.split(cmd))

    if result.stdout == "healthy":
        return True
    return False


def run_container():
    # TODO: database fixture should spin up on every new
    #       test or suite
    if not os.environ.get('CI', None):
        # client = docker.from_env()
        DOCKER_NAME = 'pytest-pgtap'
        DOCKER_IMAGE = 'lmergner/pgtap:latest'
        DATABASE_URI = 'postgres://postgres@{0}:5432/{1}'.format(
            urlparse(os.environ.get('DOCKER_HOST', '0.0.0.0:2975')
                     ).netloc.split(':')[0],  # host ip from docker host
            DOCKER_NAME  # database name
        )
        run(shlex.split(
            'docker run --rm -d --name %s -p 5432:5432 ' % DOCKER_IMAGE))

        while not db_is_running(DOCKER_NAME):
            time.sleep(15)

        run('psql --dbname ' + DATABASE_URI + ' -f tests/setup.sql')
        yield 'postgres://postgres@192.168.1.68/pytest-pgtap'
        run(shlex.split('docker stop %s' % DOCKER_NAME))


@pytest.fixture(scope='session')
def database():
    if os.environ.get('CI'):
        return os.environ.get('DATABASE_URL')
    return 'postgres://postgres@192.168.1.68/pytest-pgtap'


@pytest.fixture
def subprocess(mocker):
    # Mock the subprocess and make sure it returns

    def with_return_value(value: int=0, stdout: str=''):
        mock = mocker.patch(
            'subprocess.run', return_value=CompletedProcess(None, returncode=0))
        mock.returncode.return_value = value
        mock.stdout = ''
        return mock
    return with_return_value
