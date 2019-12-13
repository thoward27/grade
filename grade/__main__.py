import click

from grade.cli import run, report


@click.group()
def cli():
    pass


cli.add_command(run.run)
cli.add_command(report.report)

if __name__ == "__main__":
    cli()
