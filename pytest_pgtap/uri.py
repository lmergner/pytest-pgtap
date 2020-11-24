# -*- coding: utf-8 -*-
# Copyright (c) 2018 Luke Mergner and contributors
# Note:  much of this module is from SqlAlchemy and Michael Bayer
# https://bitbucket.org/zzzeek/sqlalchemy/src/1ed3803654c122f91d5910adf4078627464b0692/lib/sqlalchemy/engine/url.py
"""
    Database URI parsing, 90% borrowed from SQLAlchemy lib/sqlalchemy/engine/url.py
"""
import collections
import re
from typing import Union
from urllib.parse import parse_qsl, unquote, unquote_plus


def make_url(name_or_url: str):
    """Given a string or unicode instance, produce a new URL instance.

    The given string is parsed according to the RFC 1738 spec.  If an
    existing URL object is passed, just returns the object.
    """

    if isinstance(name_or_url, (str, bytes)):
        return _parse_rfc1738_args(name_or_url)
    elif isinstance(name_or_url, dict):
        return URL("postgres", **name_or_url)
    else:
        return URL("postgres")


class URL(object):
    """
    Represent the components of a URL used to connect to a database.

    This object is suitable to be passed directly to a
    :func:`~sqlalchemy.create_engine` call.  The fields of the URL are parsed
    from a string by the :func:`.make_url` function.  the string
    format of the URL is an RFC-1738-style string.

    All initialization parameters are available as public attributes.

    :param drivername: the name of the database backend.
      This name will correspond to a module in sqlalchemy/databases
      or a third party plug-in.

    :param username: The user name.

    :param password: database password.

    :param host: The name of the host.

    :param port: The port number.

    :param database: The database name.

    :param query: A dictionary of options to be passed to the
      dialect and/or the DBAPI upon connect.

    """

    def __init__(
        self,
        drivername: str,
        username: str = None,
        password: str = None,
        host: str = None,
        port: str = None,
        database: str = None,
        query: Union[dict, None] = None,
    ) -> None:
        self.drivername = drivername
        self.username = username
        self.password_original = password
        self.host = host
        if port is not None:
            self.port: Union[int, None] = int(port)
        else:
            self.port = None
        self.database = database
        self.query = query or {}

    @property
    def password(self):
        """ password proxy """
        if self.password_original is None:
            return None
        return str(self.password_original)

    @password.setter
    def password(self, password):
        """ password proxy setter """
        self.password_original = password

    def __str__(self):
        return self.__to_string__(hide_password=False)

    def __repr__(self):
        return self.__to_string__()

    def __hash__(self):
        return hash(str(self))

    def translate_connect_args(self):
        """Translate url attributes into a dictionary of connection arguments.

        Returns attributes of this url (`host`, `database`, `username`,
        `password`, `port`) as a plain dictionary.  The attribute names are
        used as the keys by default.  Unset or false attributes are omitted
        from the final dictionary.
        """

        translated = {}
        attribute_names = ["host", "database", "username", "password", "port"]
        for name in attribute_names:
            if getattr(self, name, False):
                translated[name] = getattr(self, name)
        return translated

    def __to_string__(self, hide_password=True) -> str:
        """ return self as a valid database uri """
        fragment = self.drivername + "://"
        if self.username is not None:
            fragment += _rfc_1738_quote(self.username)
            if self.password is not None:
                fragment += ":" + (
                    "***" if hide_password else _rfc_1738_quote(self.password)
                )
            fragment += "@"
        if self.host is not None:
            if ":" in self.host:
                fragment += "[%s]" % self.host
            else:
                fragment += self.host
        if self.port is not None:
            fragment += ":" + str(self.port)
        if self.database is not None:
            fragment += "/" + self.database
        if self.query:
            keys = list(self.query)
            keys.sort()
            fragment += "?" + "&".join(
                "%s=%s" % (k, element)
                for k in keys
                for element in _to_list(self.query[k])
            )
        return fragment


def _parse_string_to_map(name):
    pattern = re.compile(
        r"""
        (?P<drivername>[\w\+]+)://
        (?:
            (?P<username>[^:/]*)
            (?::(?P<password>[^/]*))?
        @)?
        (?:
           (?:
                \[(?P<ipv6host>[^/]+)\] |
                (?P<ipv4host>[^/:]+)
            )?
            (?::(?P<port>[^/]*))?
            )?
            (?:/(?P<database>.*))?
        """,
        re.X,
    )
    match = pattern.match(name)
    if match is not None:
        components = match.groupdict()

        if components["database"] is not None:
            tokens = components["database"].split("?", 2)
            components["database"] = tokens[0]
            if len(tokens) > 1:
                query = {}
                # note: parse.qsl in sqla
                for key, value in parse_qsl(tokens[1]):
                    if key in query:
                        query[key] = _to_list(query[key])
                        query[key].append(value)
                    else:
                        query[key] = value
            else:
                query = None
        else:
            query = None
        components["query"] = query

        if components["username"] is not None:
            components["username"] = unquote(components["username"])
        if components["password"] is not None:
            components["password"] = unquote_plus(components["password"])

        ipv4host = components.pop("ipv4host")
        ipv6host = components.pop("ipv6host")
        components["host"] = ipv4host or ipv6host

        drivername = components.pop("drivername")
        return URL(drivername, **components)
    else:
        raise Exception(
            "Could not parse rfc1738 URL from string '%s', the format "
            "should match 'dialect+driver://username:password@host:port/database'"
            % name
        )


def _rfc_1738_quote(text):
    return re.sub(r"[:@/]", lambda m: "%%%X" % ord(m.group(0)), text)


def _to_list(listlike: Union[str, list], default=None) -> list:
    if listlike is None:
        return default
    if not isinstance(listlike, collections.abc.Iterable) or isinstance(
        listlike, (str, bytes)
    ):
        return [listlike]
    elif isinstance(listlike, list):
        return listlike
    else:
        return list(listlike)


_parse_rfc1738_args = _parse_string_to_map  # pragma: no cover
