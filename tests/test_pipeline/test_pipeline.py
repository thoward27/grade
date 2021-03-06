""" Tests for the pipeline module.
"""

import unittest

from grade.pipeline import (
    Lambda,
    Pipeline,
    Run,
    AssertExitFailure,
    AssertExitSuccess,
    AssertValgrindSuccess,
    WriteOutputs,
    CompletedProcess,
)


class TestPipeline(unittest.TestCase):
    def test_fails(self):
        with self.assertRaises(AssertionError):
            Pipeline(Run(["ls"]), AssertExitFailure())()

    def test_fail_multiple(self):
        with self.assertRaises(AssertionError):
            tests = map(lambda t: Pipeline(Run(["ls"]), AssertExitFailure()), range(10))
            [test() for test in tests]

    @staticmethod
    def test_passes():
        Pipeline(Run(["ls"]), AssertExitSuccess())

    @staticmethod
    def test_pass_multiple():
        tests = map(lambda t: Pipeline(Run(["ls"]), AssertExitSuccess()), range(10))
        [test() for test in tests]

    def test_iteration(self):
        pipeline = Pipeline(
            Run(["ls"]), AssertExitSuccess(), AssertValgrindSuccess(), WriteOutputs("temp"),
        )
        [self.assertTrue(callable(callback)) for callback in pipeline]
        self.assertIsInstance(pipeline[1], AssertExitSuccess)
        self.assertEqual(len(pipeline), 4)


class TestLambda(unittest.TestCase):
    def test_simple(self):
        """ Lambda that does return completedprocess. """
        results = Run(["ls"])()
        results = Lambda(lambda r: r)(results)
        self.assertIsInstance(results, CompletedProcess)

    @staticmethod
    def randomFunction(results):
        """ Function for the test below. """
        return results

    def test_passing_function(self):
        """ Lambda that executes a function. """
        results = Run(["ls"])()
        results = Lambda(self.randomFunction)(results)
        self.assertIsInstance(results, CompletedProcess)
