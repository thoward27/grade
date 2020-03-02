import time
from functools import partial
from subprocess import run, PIPE, TimeoutExpired

from .completedprocess import CompletedProcess


class Run:
    """ Runs the given command.

    This is the recommended way to start a Pipeline, as it generates
    a CompletedProcess object to pass down the chain.

    You can pass anything to this that you would pass to subprocess.run(),
    plus one additional note: input can take a callable function. If you choose
    to pass a callable to input, you can make use of the CompletedProcess object.

    An example of passing a callable to input:

    >>> Pipeline(
        Run(['cat', 'README.md']),
        Run(['grep', 'pip'], input=lambda r: r.stdout),
        AssertStdoutMatches('python -m pip install grade')
    )()

    This essentially allows you to chain the output of previous calls to future
    calls in the pipeline.
    """

    _run = partial(run, stderr=PIPE, stdout=PIPE, timeout=60 * 10, encoding="utf-8", errors="ignore")

    def run(self, command, **kwargs):
        results = self._run(command, **kwargs)
        return CompletedProcess(results)

    def __init__(self, command, input=None, **kwargs):
        self.command = command
        self.input = input
        self.kwargs = kwargs
        return

    def __call__(self, results: CompletedProcess = None) -> CompletedProcess:
        if callable(self.input):
            self.input = self.input(results)
        try:
            start = time.time()
            results: CompletedProcess = self.run(self.command, input=self.input, **self.kwargs)
            duration = time.time() - start
        except TimeoutExpired:
            raise TimeoutError(f"{self.command} timed out.")
        else:
            results.duration = duration
            return results
