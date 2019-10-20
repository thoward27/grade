import json
import sys
import time
from typing import Optional, TextIO, Type
from unittest import registerResult, TextTestRunner
import io
import time

from grade.result import Result

class GradedRunner(TextTestRunner):
    def __init__(self,
                 stream: Optional[TextIO] = io.StringIO(),
                 descriptions: bool = True,
                 verbosity: int = 0,
                 failfast: bool = False,
                 buffer: bool = True,
                 warnings: Optional[Type[Warning]] = None,
                 *,
                 tb_locals: bool = False,
                 visibility: 'str' = 'visible') -> None:
        super().__init__(stream, descriptions, verbosity, failfast, buffer, Result, warnings, tb_locals=tb_locals)
        self.visibility = visibility
    
    def run(self, test):
        start = time.time()
        results = super().run(test)
        results.data['execution_time'] = round(time.time() - start)
        results.data['visibility'] = self.visibility
        return results
