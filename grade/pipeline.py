""" Pipeline. 
"""
import logging
from functools import partial
from os import path
from subprocess import run, PIPE, CompletedProcess
from typing import List


class Pipeline:
    def __init__(self, *callbacks):
        self.callbacks = callbacks

    def __call__(self):
        results = None
        for callback in self.callbacks:
            results = callback(results)
        return results

    def __iter__(self):
        for callback in self.callbacks:
            yield callback

    def __getitem__(self, index):
        return self.callbacks[index]

    def __len__(self):
        return len(self.callbacks)


class PartialCredit:
    def __init__(self, pipelines: List[Pipeline], value: int):
        self.pipelines = list(pipelines)
        self.value = value
        self._score = 0
        self._executed = False

    @property
    def score(self) -> float:
        assert (self._executed)
        return min(self.value, round(self._score, 2))

    def __call__(self):
        self._executed = True
        for pipeline in self.pipelines:
            try:
                pipeline()
            except Exception as e:
                # TODO: Figure out how to raise this properly in caller.
                logging.exception(e, exc_info=False)
            else:
                self._score += self.value / len(self.pipelines)
        return self


class AssertExitSuccess:
    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if results.returncode != 0:
            raise AssertionError(
                f'{results.args} did not exit successfully. {results.returncode}\n{results.stdout}\n{results.stderr}')
        return results


class AssertExitFailure:
    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        if results.returncode == 0:
            raise AssertionError(f'{results.args} exited successfully.')
        return results


class AssertValgrindSuccess:
    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        # TODO: add --exit-on-first-error=yes when valgrind --version>=3.14
        results = Run(['valgrind', '-q', '--error-exitcode=1', *results.args])()
        results = AssertExitSuccess()(results)
        return results


class AssertStdoutMatches:
    @staticmethod
    def hasStdout(filepath):
        return path.exists(filepath) and path.exists(filepath + '.stdout')

    def __call__(self, results: CompletedProcess, stdout: str = None) -> CompletedProcess:
        if stdout is None:
            stdout = filter(self.hasStdout, results.args)
            assert (len(stdout) == 1)
            with open(stdout[0] + '.stdout', 'r') as f:
                stdout = f.read()

        if results.stdout.strip() != stdout.strip():
            raise AssertionError(
                f'{results.args} stdout does not match expected. {results.stdout}')


class AssertStderrMatches:
    @staticmethod
    def hasStdout(filepath):
        return path.exists(filepath) and path.exists(filepath + '.stderr')

    def __call__(self, results: CompletedProcess, stderr: str = None) -> CompletedProcess:
        if stderr is None:
            stderr = filter(self.hasStdout, results.args)
            assert (len(stderr) == 1)
            with open(stderr[0] + '.stderr', 'r') as f:
                stderr = f.read()

        if results.stderr.strip() != stderr.strip():
            raise AssertionError(
                f'{results.args} stderr does not match expected.')


class Run:
    run = partial(
        run,
        stderr=PIPE,
        stdout=PIPE,
        timeout=60 * 10,
        encoding='utf-8',
        errors='ignore'
    )

    def __init__(self, command, **kwargs):
        self.command = command
        self.kwargs = kwargs

    def __call__(self, results: CompletedProcess = None, **kwargs) -> CompletedProcess:
        self.kwargs.update(kwargs)
        return self.run(self.command, **self.kwargs)


class WriteStdout:
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
    def __call__(self, results, testcase):
        WriteStdout(testcase + '.stdout', True)(results)
        WriteStderr(testcase + '.stderr', True)(results)
        return results
