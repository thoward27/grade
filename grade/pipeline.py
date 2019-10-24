""" Pipeline: Autograding Executable Files

Pipeline components allow you chain together tests
for executable files within a few lines, without the
headaches of typical executable testing.
"""
import logging
from functools import partial
from os import path
from subprocess import run, PIPE, CompletedProcess
from typing import Callable, Iterator

Callback = Callable[[CompletedProcess], CompletedProcess]


class Pipeline:
    """ Takes callbacks and executes them sequentially when called.

    Used for grading executable files or scripts, as it allows
    you to chain together Run() with things like AssertExitSuccess().

    It does this by passing a CompletedProcess object to each successive
    callback, allowing each callback to modify or replace it during 
    execution of the pipeline. 

    All Pipelines should start with a call to Run().

    Raises an exception if any assertions or run commands fail.
    """

    def __init__(self, *callbacks: Callback):
        self.callbacks = callbacks

    def __call__(self) -> CompletedProcess:
        results = None
        for callback in self.callbacks:
            results = callback(results)
        return results

    def __iter__(self) -> Callback:
        for callback in self.callbacks:
            yield callback

    def __getitem__(self, index) -> Callback:
        return self.callbacks[index]

    def __len__(self) -> int:
        return len(self.callbacks)


class PartialCredit:
    """ Executes a list of pipelines, assigning credit for each successful run.

    Divides the value given across all pipelines, giving equal weight 
    to each pipeline in the list.

    # TODO: Provide a weighting mechanism.
    """

    def __init__(self, pipelines: Iterator[Pipeline], value: int):
        self.pipelines = list(pipelines)
        self.value = value
        self._score = 0
        self._executed = False

    @property
    def score(self) -> float:
        """ Returns the aggregate score, raises exception if not run. """
        assert self._executed
        return min(self.value, round(self._score, 2))

    def __call__(self):
        self._executed = True
        for pipeline in self.pipelines:
            try:
                pipeline()
            except Exception as e:
                logging.exception(e, exc_info=False)
            else:
                self._score += self.value / len(self.pipelines)
        return self


class AssertExitSuccess:
    """ Asserts that the CompletedProcess exited successfully. """

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if results.returncode != 0:
            raise AssertionError(
                f'{results.args} should have exited successfully. {results.returncode} != 0')
        return results


class AssertExitFailure:
    """ Asserts that the CompletedProcess exited unsuccessfully. """

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if results.returncode == 0:
            raise AssertionError(f'{results.args} should have exited unsuccessfully.')
        return results


class AssertValgrindSuccess:
    """ Asserts that there are no valgrind errors reported. """

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        # TODO: add --exit-on-first-error=yes when valgrind --version>=3.14
        if type(results.args) is list:
            results = Run(
                ['valgrind', '-q', '--error-exitcode=1', *results.args])()
        elif type(results.args) is str:
            results = Run(
                f'valgrind -q --error-exitcode=1 {results.args}', shell=True)()
        results = AssertExitSuccess()(results)
        return results


class AssertStdoutMatches:
    """ Asserts that the program's stdout matches expected. 

    Expected stdout can be provided in 3 major ways:
        - Specify the stdout directly as a string.
        - Specify the stdout as a filepath, which is read for stdout content
        - Specify neither, and it will look through the files contained in
          CompletedProcess.args for a file that has a counterpart named 
          file.stdout, which it will take and use as stdout.
    """

    def __init__(self, stdout: str = None, filepath: str = None):
        if stdout and filepath:
            raise ValueError("Can only pass one of stdout or filepath.")
        elif filepath:
            with open(filepath, 'r') as f:
                self.stdout = f.read()
        else:
            self.stdout = stdout

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if self.stdout is not None:
            pass
        elif type(results.args) is list:
            self.stdout = list(
                filter(lambda f: path.exists(f + '.stdout'), results.args))
            assert (len(self.stdout) == 1)
            with open(self.stdout[0] + '.stdout', 'r') as f:
                self.stdout = f.read()
        else:
            raise ValueError(f"Cannot infer stdout file for {results.args}")

        if results.stdout.strip() != self.stdout.strip():
            raise AssertionError(
                f'{results.args} stdout does not match expected.\n{self.stdout.strip()} !=\n{results.stdout.strip()}')

        return results


class AssertStderrMatches:
    """ Asserts that the program's stderr matches expected.

    Expected stderr can be provided in 3 major ways:
        - Specify the stderr directly as a string
        - Specify the stderr as a filepath, which is read for stderr content
        - Specify neither, and it will look through the files contained in
          CompletedProcess.args for a file that has a counterpart named
          file.stderr, which it will take an use as stderr.
    """

    def __init__(self, stderr: str = None, filepath: str = None):
        if stderr and filepath:
            raise ValueError("Can only pass one of stderr and filepath.")
        elif filepath:
            with open(filepath, 'r') as f:
                self.stderr = f.read()
        else:
            self.stderr = stderr

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if self.stderr is not None:
            pass

        elif type(results.args) is list:
            self.stderr = list(filter(lambda f: path.exists(f + '.stderr'), results.args))
            assert (len(self.stderr) == 1)
            with open(self.stderr[0] + '.stderr', 'r') as f:
                self.stderr = f.read()

        else:
            raise ValueError(f"Cannot infer stderr file of {results.args}")

        if results.stderr.strip() != self.stderr.strip():
            raise AssertionError(
                f'{results.args} stderr does not match expected.\n{self.stderr.strip()} !=\n{results.stderr.strip()}')

        return results


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

    _run = partial(
        run,
        stderr=PIPE,
        stdout=PIPE,
        timeout=60 * 10,
        encoding='utf-8',
        errors='ignore'
    )

    def __init__(self, command, input=None, **kwargs):
        self.command = command
        self.input = input
        self.kwargs = kwargs

    def __call__(self, results: CompletedProcess = None) -> CompletedProcess:
        if callable(self.input):
            self.input = self.input(results)

        return self._run(self.command, input=self.input, **self.kwargs)


class Lambda:
    """ Execute arbitrary code in a Pipeline. """

    def __init__(self, function: Callback):
        self.function = function

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        results = self.function(results)
        if type(results) is not CompletedProcess:
            raise TypeError('Lambda did not return CompletedProcess.')
        return results


class WriteStdout:
    """ Writes the current stdout to the given file. 

    File defaults to ./temp
    """

    def __init__(self, filepath: str = 'temp', overwrite: bool = True):
        self.filepath = filepath
        self.overwrite = overwrite

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if path.exists(self.filepath) and self.overwrite is False:
            raise FileExistsError

        with open(self.filepath, 'w') as f:
            f.write(results.stdout)

        return results


class WriteStderr:
    """ Writes the current stderr to the given file.

    File defaults to ./temp
    """

    def __init__(self, filepath: str = 'temp', overwrite: bool = True):
        self.filepath = filepath
        self.overwrite = overwrite

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if path.exists(self.filepath) and self.overwrite is False:
            raise FileExistsError

        with open(self.filepath, 'w') as f:
            f.write(results.stderr)

        return results


class WriteOutputs:
    """ Writes both outputs to files that can be inferred in a Pipeline.

    This is mostly useful for creating testcases, it creates output files
    that can be inferred by the AssertStdoutMatches and AssertStderrMatches
    callbacks.
    """

    def __init__(self, testcase):
        self.testcase = testcase

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        WriteStdout(self.testcase + '.stdout', True)(results)
        WriteStderr(self.testcase + '.stderr', True)(results)
        return results
