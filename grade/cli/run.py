import json
import unittest

import click

from grade.runners import GradedRunner


@click.command()
@click.option("--batch/--single", default=False)
@click.option("--context", default=".")
@click.option("-p", "--pattern", default="test*")
def run(batch, context, pattern):
    """ Run the autograder. """
    suite = unittest.defaultTestLoader.discover(context, pattern=pattern)
    results = GradedRunner(visibility="visible").run(suite)
    with open(".grade", "w") as f:
        json.dump(results.data, f, indent=4)
