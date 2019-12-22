from subprocess import CompletedProcess as Subprocess
from typing import Union


class CompletedProcess:
    def __init__(self, process: Subprocess):
        self.process: Subprocess = process
        # TODO: Duration should be a stack of durations for each run call.
        self.duration: Union[float, None] = None
        return

    @property
    def stderr(self):
        return self.process.stderr

    @property
    def stdout(self):
        return self.process.stdout

    @property
    def args(self):
        return self.process.args

    @property
    def returncode(self):
        return self.process.returncode

    @returncode.setter
    def returncode(self, value):
        self.process.returncode = value
        return
