# Copyright (c) 2018 Luke Mergner and contributors

import pytest
from subprocess import CompletedProcess


@pytest.fixture
def database():
    # TODO: database fixture should spin up on every new
    #       test or suite
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
