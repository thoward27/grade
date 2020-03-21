import json
import sys
import unittest

from grade.pipeline import (
    Run,
    AssertExitSuccess,
    Pipeline,
    AssertStdoutMatches,
    AssertStderrMatches,
    AssertStdoutContains,
    Lambda,
)

PYTHON = sys.executable


class TestMain(unittest.TestCase):
    @staticmethod
    def test_no_arguments():
        Pipeline(
            Run([PYTHON, "-m", "grade"]), AssertExitSuccess(),
        )
        return

    @staticmethod
    def test_successful_no_output():
        Pipeline(
            Run([PYTHON, "-m", "grade", "run", "-p", "test_mixins.py"]),
            AssertExitSuccess(),
            AssertStdoutMatches(""),
            AssertStderrMatches(""),
        )()

    def test_json_output(self):
        Pipeline(
            Run([PYTHON, "-m", "grade", "run", "-p", "test_mixins.py"]),
            Run([PYTHON, "-m", "grade", "report", "json", "-"]),
            AssertExitSuccess(),
            AssertStdoutContains(["tests"]),
            Lambda(lambda results: self.assertGreater(len(json.loads(results.stdout)["tests"]), 3)),
        )()
