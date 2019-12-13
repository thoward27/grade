from os import path

from .completedprocess import CompletedProcess


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
