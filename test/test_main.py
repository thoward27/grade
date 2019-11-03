import json
import unittest

from grade.pipeline import *


class TestMain(unittest.TestCase):

    def test_successful_no_output(self):
        Pipeline(
            Run(['python', '-m', 'grade', '.', '-p', 'test_mixins.py']),
            AssertExitSuccess(),
            AssertStdoutMatches(''),
            AssertStderrMatches('WARNING:root:No output directive found. Ran successfully.'),
        )()

    def test_json_output(self):
        Pipeline(
            Run(['python', '-m', 'grade', '.', '-p', 'test_mixins.py', '--json']),
            Lambda(lambda results: self.assertGreater(len(json.loads(results.stdout)['tests']), 3))
        )()
