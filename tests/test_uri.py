# -*- coding: utf-8 -*-
# Copyright (c) 2018 Luke Mergner and contributors
# Note:  much of this test is from SqlAlchemy and Michael Bayer
# https://bitbucket.org/zzzeek/sqlalchemy/src/1ed3803654c122f91d5910adf4078627464b0692/test/engine/test_parseconnect.py?at=master&fileviewer=file-view-default

import pytest
from pytest_pgtap.uri import _parse_string_to_map


@pytest.mark.parametrize(
    "text",
    [
        "dbtype://username:password@hostspec:110//usr/db_file.db",
        "dbtype://username:password@hostspec/database",
        "dbtype+apitype://username:password@hostspec/database",
        "dbtype://username:password@hostspec",
        "dbtype://username:password@/database",
        "dbtype://username@hostspec",
        "dbtype://username:password@127.0.0.1:1521",
        "dbtype://hostspec/database",
        "dbtype://hostspec",
        "dbtype://hostspec/?arg1=val1&arg2=val2",
        "dbtype+apitype:///database",
        "dbtype:///:memory:",
        "dbtype:///foo/bar/im/a/file",
        "dbtype:///E:/work/src/LEM/db/hello.db",
        "dbtype:///E:/work/src/LEM/db/hello.db?foo=bar&hoho=lala",
        "dbtype:///E:/work/src/LEM/db/hello.db?foo=bar&hoho=lala&hoho=bat",
        "dbtype://",
        "dbtype://username:password@/database",
        "dbtype:////usr/local/_xtest@example.com/members.db",
        "dbtype://username:apples%2Foranges@hostspec/database",
        "dbtype://username:password@[2001:da8:2004:1000:202:116:160:90]"
        "/database?foo=bar",
        "dbtype://username:password@[2001:da8:2004:1000:202:116:160:90]:80"
        "/database?foo=bar",
    ],
)
def test_rfc1738(text):

    u = _parse_string_to_map(text)
    assert u.drivername in ("dbtype", "dbtype+apitype")
    assert u.username in ("username", None)
    assert u.password in ("password", "apples/oranges", None)
    assert u.host in (
        "hostspec",
        "127.0.0.1",
        "2001:da8:2004:1000:202:116:160:90",
        "",
        None,
    ), u.host
    assert u.database in (
        "database",
        "/usr/local/_xtest@example.com/members.db",
        "/usr/db_file.db",
        ":memory:",
        "",
        "foo/bar/im/a/file",
        "E:/work/src/LEM/db/hello.db",
        None,
    ), u.database
    assert str(u) == text
