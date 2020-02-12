""" Run.

Handles running the test suite and saving results.
"""

import json
import unittest

import click

from grade.runners import GradedRunner


@click.command(short_help="runs the test suite")
@click.option("--context", default=".", help="context to run tests from")
@click.option("-p", "--pattern", default="test*", help="pattern to find files with")
def run(context, pattern):
    """ Run the autograder. """
    suite = unittest.defaultTestLoader.discover(context, pattern=pattern)
    results = GradedRunner(visibility="visible").run(suite)
    with open(".grade", "w") as f:
        json.dump(results.data, f, indent=4)
