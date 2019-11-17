import unittest

import click

from grade.runners import GradedRunner
import json

@click.command()
@click.option('--batch/--single', default=False)
@click.option('--context', default='.')
@click.option('-p', '--pattern', default="test*")
def run(batch, context, pattern):
    suite = unittest.defaultTestLoader.discover(context, pattern=pattern)
    results = GradedRunner(visibility='visible').run(suite)
    with open('.grade', 'w') as f:
        f.write(json.dumps(results.data))
