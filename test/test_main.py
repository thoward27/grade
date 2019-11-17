import json
import unittest

from grade.pipeline import *


class TestMain(unittest.TestCase):

    def test_successful_no_output(self):
        Pipeline(
            Run(['python', '-m', 'grade', 'run', '-p', 'test_mixins.py']),
            AssertExitSuccess(),
            AssertStdoutMatches(''),
            AssertStderrMatches(''),
        )()

    def test_json_output(self):
        Pipeline(
            Run(['python', '-m', 'grade', 'run']),
            Run(['python', '-m', 'grade', 'report', 'json', '-']),
            AssertStdoutContains(['tests']),
            Lambda(lambda results: self.assertGreater(len(json.loads(results.stdout)['tests']), 3))
        )()
