import sys

import click

@click.command()
@click.argument('output', type=click.File('w'))
@click.option('--rcfile', nargs=1, default=None)
def report(output: str, rcfile: str):
    with open('.grade') as f:
        grades = eval(f.read())
    output.write(str(grades))
