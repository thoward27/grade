"""Result reporting.

This handles the CLI interface for reporting results.
"""

import click
import json


@click.command(short_help="writes results to either stdout or an output file")
@click.option(
    "--format",
    type=click.Choice({"json", "markdown", "gradescope"}),
    default="markdown",
    help="output format to use",
)
@click.option(
    "--output", type=click.File("w"), default="-", help="optional file to write output to"
)
def report(format, output):
    """ Report in the default format to stdout. """
    with open(".grade", "r") as fp:
        grades = json.load(fp)

    if format == "markdown":
        score, max_score = (
            sum((t["score"] for t in grades["tests"])),
            sum((t["max_score"] for t in grades["tests"])),
        )
        output.write(
            "\n\n".join(
                [
                    f"# Grade Results",
                    f"## Autograder Score: {score}/{max_score}",
                    *[
                        "\n".join(
                            [
                                f"### {test['name']} {test['score']}/{test['max_score']}",
                                "",
                                f"{test['output'] if 'output' in test else ''}",
                            ]
                        )
                        for test in grades["tests"]
                    ],
                ]
            )
        )

    elif format == "gradescope":
        output.write(json.dumps(grades, indent=4, sort_keys=True))

    elif format == "json":
        output.write(json.dumps(grades))

    else:
        print(str(grades))
