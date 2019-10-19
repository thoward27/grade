import json
import sys
import time
from typing import Optional, TextIO, Type
from unittest import registerResult, TextTestRunner
import io
import time

from grade.result import Result

class Stream(io.StringIO):
    def writeln(self, arg=None, /):
        if arg:
            self.write(arg)
        self.write('\n')

class GradedRunner(TextTestRunner):
    def __init__(self,
                 stream: Optional[TextIO] = None,
                 descriptions: bool = True,
                 verbosity: int = 1,
                 failfast: bool = False,
                 buffer: bool = True,
                 warnings: Optional[Type[Warning]] = None,
                 *,
                 tb_locals: bool = False,
                 visibility: 'str' = 'visible') -> None:
        super().__init__(stream, descriptions, verbosity, failfast, buffer, Result, warnings, tb_locals=tb_locals)
        self.visibility = visibility
        self.stream = Stream()
    
    def run(self, test):
        start = time.time()
        results = super().run(test)
        results.data['execution_time'] = round(time.time() - start)
        results.data['visibility'] = self.visibility
        return results
