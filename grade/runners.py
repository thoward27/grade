import json
import sys
import time
from typing import Optional, TextIO, Type
from unittest import registerResult, TextTestRunner
import io
import time

from grade.result import TestResult, JSONResult

class Stream(io.StringIO):
    def writeln(self, arg=None, /):
        if arg:
            self.write(arg)
        self.write('\n')

class JSONRunner(TextTestRunner):
    def __init__(self,
                 stream: Optional[TextIO] = None,
                 descriptions: bool = True,
                 verbosity: int = 1,
                 failfast: bool = False,
                 buffer: bool = False,
                 resultclass=JSONResult,
                 warnings: Optional[Type[Warning]] = None,
                 *,
                 tb_locals: bool = False) -> None:
        super().__init__(stream, descriptions, verbosity, failfast, buffer, resultclass, warnings, tb_locals=tb_locals)
        self.stream = Stream()
    
    def run(self, test):
        start = time.time()
        results = super().run(test)
        results.data['execution_time'] = round(time.time() - start)
        return results


class MDRunner(TextTestRunner):
    pass


class _JSON:
    """A test runner class that displays results in JSON form.
    """
    resultclass = TestResult

    def __init__(self, stream=sys.stdout, descriptions=True, verbosity=1,
                 failfast=False, buffer=True, visibility=None,
                 stdout_visibility=None):
        """
        Set buffer to True to include test output in JSON
        """
        self.stream = stream
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.failfast = failfast
        self.buffer = buffer
        self.json_data = {}
        self.json_data["tests"] = []
        self.json_data["leaderboard"] = []
        if visibility:
            self.json_data["visibility"] = visibility
        if stdout_visibility:
            self.json_data["stdout_visibility"] = stdout_visibility

    def _makeResult(self):
        return self.resultclass(self.stream, self.descriptions, self.verbosity,
                                self.json_data["tests"], self.json_data["leaderboard"])

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        startTime = time.time()
        startTestRun = getattr(result, 'startTestRun', None)
        if startTestRun is not None:
            startTestRun()
        try:
            test(result)
        finally:
            stopTestRun = getattr(result, 'stopTestRun', None)
            if stopTestRun is not None:
                stopTestRun()
        stopTime = time.time()
        timeTaken = stopTime - startTime

        self.json_data["execution_time"] = format(timeTaken, "0.2f")

        total_score = 0
        for test in self.json_data["tests"]:
            total_score += test["score"]
        self.json_data["score"] = total_score

        json.dump(self.json_data, self.stream, indent=4)
        self.stream.write('\n')
        return result
