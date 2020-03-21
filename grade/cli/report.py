import click

GRADES = {}


def load():
    with open(".grade", "r") as f:
        grades = eval(f.read())
    return grades


def score():
    # TODO: This should be stored in original output.
    return (sum(test["score"] for test in GRADES["tests"]), sum(test["max_score"] for test in GRADES["tests"]))


@click.group(invoke_without_command=True)
@click.pass_context
def report(ctx):
    """ Report in the default format to stdout. """
    global GRADES
    GRADES = load()
    if ctx.invoked_subcommand is None:
        print(str(GRADES))


@report.command()
@click.argument("output", type=click.File("w"), default="-")
def gradescope(output):
    json(output)
    return


@report.command()
@click.argument("output", type=click.File("w"), default="-")
def json(output):
    import json

    output.write(json.dumps(GRADES, indent=4, sort_keys=True))
    return


@report.command()
@click.argument("output", type=click.File("w"), default="-")
def markdown(output):
    output.write(
        "\n\n".join(
            [
                f"# Grade Results",
                f"## Autograder Score: {'/'.join(map(str, score()))}",
                *[
                    f"### {test['name']} {test['score']}/{test['max_score']}\n\n{test['output'] if 'output' in test else ''}"
                    for test in GRADES["tests"]
                ],
            ]
        )
    )
    return
