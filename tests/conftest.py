# -*- coding: utf-8 -*-
# Copyright (c) 2018 Luke Mergner

import os
from subprocess import CompletedProcess, run
from urllib.parse import urlparse

import pytest


@pytest.fixture(scope="session")
def database():
    return os.environ.get("DATABASE_URL")


@pytest.fixture
def subprocess(mocker):
    """ Mock the subprocess and make sure it returns a value """

    def with_return_value(value: int = 0, stdout: str = ""):
        mock = mocker.patch(
            "subprocess.run", return_value=CompletedProcess(None, returncode=0)
        )
        mock.returncode.return_value = value
        mock.stdout = stdout
        return mock

    return with_return_value
