import unittest

from grade.pipeline import *


class TestPartialCredit(unittest.TestCase):

    def test_full_credit(self):
        pipelines = map(lambda t: Pipeline(Run(['ls'])), range(10))
        results = PartialCredit(pipelines, 10)()
        self.assertEqual(results.score, 10)
        return

    def test_partial_credit(self):
        pipelines = map(lambda t: Pipeline(Run([t]), AssertExitSuccess()), ['ls', 'void'])
        with self.assertLogs() as logs:
            results = PartialCredit(pipelines, 10)()
        self.assertIn("ERROR:root:", logs.output[0])
        self.assertEqual(results.score, 5)
        return

    def test_no_credit(self):
        pipelines = map(lambda t: Pipeline(Run(['ls']), AssertExitFailure()), range(10))
        with self.assertLogs() as logs:
            results = PartialCredit(pipelines, 10)()
        self.assertEqual(10, len(logs.output))
        self.assertIn("ERROR:root:['ls'] should have exited unsuccessfully.", logs.output)
        self.assertEqual(results.score, 0)
        return
