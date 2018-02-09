#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from pytest_pgtap.plugin import _is_test

test_string = "SELECT has_column('whatever.contact', 'name', 'contacts should have a name');"


def test_filter():
    with open('tests/test_from_file.sql') as tf:
        sql = tf.readlines()

    result = [x for x in sql if _is_test(x)]
    assert len(result) == 2
    assert result[0].strip() == test_string

