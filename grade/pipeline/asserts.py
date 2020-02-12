import logging
import re
from os import path
from typing import List, Pattern

from .completedprocess import CompletedProcess
from .pipeline import Callback
from .run import Run

log = logging.getLogger(__file__)


class Check:
    """ Prevents raising exceptions, alters returncode instead.

    Wrap any assertion in this to make it a "check" instead of an
    assert. Check does not raise an exception, but rather alters the
    returncode to match what the assertion would have done.
    """

    def __init__(self, callback: Callback):
        self.callback = callback

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        try:
            self.callback(results)
        except AssertionError:
            results.returncode += 1
            results.stdout.write(f'Check Failed!\n{self.callback} raised an exception!')
        else:
            results.returncode = 0
        finally:
            return results


class Not:
    """ Negates the enclosed callback.

    If the enclosed callback throws an exception,
    results are returned successfully.
    If the enclosed callback does not throw an exception,
    an assertion error is raised.
    """
    def __init__(self, callback: Callback):
        self.callback = callback
        return

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        try:
            self.callback(results)
        except Exception as err:
            log.debug(err)
            return results
        else:
            raise AssertionError(f'{self.callback} passed!')


class Or:
    """ Ensures that at least one of the callbacks given passes.
    """
    def __init__(self, *callbacks):
        self.callbacks = callbacks
        return

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        for callback in self.callbacks:
            try:
                results = callback(results)
            except Exception as err:
                log.debug(err)
            else:
                return results
        raise AssertionError(f'None of the callbacks passed! [{[str(c) for c in self.callbacks]}]')


class AssertFaster:
    """ Asserts that the most recent call to Run() was faster than duration.
    """
    def __init__(self, duration):
        self.duration = duration
        return

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if results.duration > self.duration:
            raise AssertionError(f'{results.args} took longer than {self.duration}')
        return results


class AssertExitSuccess:
    """ Asserts that the CompletedProcess exited successfully. """

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if results.returncode != 0:
            raise AssertionError('\n'.join([
                f'{results.args} should have exited successfully. {results.returncode} != 0',
                results.stdout,
                results.stderr
            ]))
        return results


class AssertExitFailure:
    """ Asserts that the CompletedProcess exited unsuccessfully. """

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if results.returncode == 0:
            raise AssertionError(f'{results.args} should have exited unsuccessfully.')
        return results


class AssertExitStatus:
    """ Asserts that the program exited with a specific error code."""
    def __init__(self, returncode: int):
        self.returncode = returncode
        return

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if results.returncode != self.returncode:
            raise AssertionError(f'{results.args} return {results.returncode}, expected {self.returncode}')
        return results


class AssertValgrindSuccess:
    """ Asserts that there are no valgrind errors reported. """

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if type(results.args) is list:
            # TODO: Add --exit-on-first-error=yes back in when valgrind > 3.13 is available on ubuntu LTS
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


class AssertStdoutRegex:
    """ Asserts programs' stdout contains the regex pattern provided.
    """

    def __init__(self, pattern: str):
        self.pattern: Pattern = re.compile(pattern)

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if not self.pattern.search(results.stdout):
            raise AssertionError(f'{self.pattern.pattern} not found in {results.stdout}')
        return results


class AssertStderrRegex:
    """ Asserts programs' stderr contains the regex pattern provided.
    """

    def __init__(self, pattern: str):
        self.pattern: Pattern = re.compile(pattern)

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if not self.pattern.search(results.stderr):
            raise AssertionError(f'{self.pattern.pattern} not found in {results.stderr}')
        return results


class AssertStdoutContains:
    """ Asserts programs' stdout contains all of the string(s) provided.
    """

    def __init__(self, strings: List[str]):
        self.strings = strings

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if not all([s in results.stdout for s in self.strings]):
            raise AssertionError(f'One or more of {self.strings} not in {results.stdout}')
        return results


class AssertStderrContains:
    """ Assert programs' stderr contains all of the string(s) provided.
    """

    def __init__(self, strings: List[str]):
        self.strings = strings

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if not all([s in results.stderr for s in self.strings]):
            raise AssertionError(f'One or more of {self.strings} not in {results.stderr}')
        return results
