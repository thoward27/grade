""" Main interface to the CLI.
"""

import click

from grade.cli import run, report


@click.group(name="grade")
def cli():
    pass


cli.add_command(run.run)
cli.add_command(report.report)

if __name__ == "__main__":
    cli(prog_name="grade")
