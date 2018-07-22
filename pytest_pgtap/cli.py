# -*- coding: utf-8 -*-
# Copyright (c) 2018 Luke Mergner and contributors
"""
Define the command line interface for pgtap.
"""
import logging
import click
from tap.loader import Loader
from .pgtap import Runner, find_test_files


logger = logging.getLogger('pytest-pgtap')


def log_level_name(lvl, lower_bound=2):
    """ Given an integer, return a logging.LEVEL """
    levels = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG,
    }

    # offset from a reasonable amount of verbosity
    lvl += lower_bound

    # but makes sure we don't exceed the max
    upper_bound = max(levels.keys())
    if lvl > upper_bound:
        lvl = upper_bound

    return levels.get(lvl, lower_bound)


@click.command()
@click.argument(
    'path_or_file',
    type=click.Path(exists=True),
    default='tests/'
)
@click.option('--uri', default={}, help='Database uri')
@click.option(
    '-schema', default=None,
    help='the schema used for pgtap\'s runtests() function. Setting '
    'the schema tells pgtap to run runtests().'
)
@click.option('-x', '--exclude', multiple=True,)
@click.option('--verbose', '-v', count=True, default=0)
def cli(path_or_file, schema, filename, verbose, exclude, uri):
    """ Find all the pgTap test files in a directory and run them against a
    database, where PATH is the test directory. PATH is optional and defaults
    to tests/.

    """
    # TODO: add testing for file handling
    # TODO: connect exclude to find_test_files
    # TODO: Add / verify tests for excluded files
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=log_level_name(verbose))
    runner = Runner(uri)
    if path_or_file.is_file():
        files = [path_or_file]
    elif path_or_file.is_dir():
        files = find_test_files(path_or_file)
    else:
        raise click.BadArgumentUsage('Expected a file or directory')
    for fn in files:
        with open(fn) as f:
            try:
                tap_result = runner.run(f.read())
            except Exception as e:
                raise click.ClickException(e)
        l = Loader()
        suite = l.load_suite_from_text(fn, tap_result)
        import unittest
        runner = unittest.TextTestRunner(verbosity=3)
        result = runner.run(suite)
