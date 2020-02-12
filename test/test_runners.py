""" Tests for the runners module.
"""

import json
import unittest

from grade.decorators import *
from grade.mixins import *
from grade.runners import *


class TestRunner(unittest.TestCase):
    """
    Gradescope Example Output:
    { 
        "score": 44.0, // optional, but required if not on each test case below. Overrides total of tests if specified.
        "execution_time": 136, // optional, seconds
        "output": "Text relevant to the entire submission", // optional
        "visibility": "after_due_date", // Optional visibility setting
        "stdout_visibility": "visible", // Optional stdout visibility setting
        "extra_data": {}, // Optional extra data to be stored
        "tests": // Optional, but required if no top-level score
            [
                {
                    "score": 2.0, // optional, but required if not on top level submission
                    "max_score": 2.0, // optional
                    "name": "Your name here", // optional
                    "number": "1.1", // optional (will just be numbered in order of array if no number given)
                    "output": "Giant multiline string that will be placed in a <pre> tag and collapsed by default", // optional
                    "tags": ["tag1", "tag2", "tag3"], // optional
                    "visibility": "visible", // Optional visibility setting
                    "extra_data": {} // Optional extra data to be stored
                },
                // and more test cases...
            ],
        "leaderboard": // Optional, will set up leaderboards for these values
            [
                {"name": "Accuracy", "value": .926},
                {"name": "Time", "value": 15.1, "order": "asc"},
                {"name": "Stars", "value": "*****"}
            ]
    }
    """

    class TestPassing(ScoringMixin, unittest.TestCase):

        @weight(10)
        def test_full_credit(self):
            """ Testing one thing or another. """
            self.leaderboardTitle = 'Successful'
            self.leaderboardOrder = 'asc'
            self.leaderboardScore = 10

            self.assertTrue(True)
            print("Output when successful")
            return

        def test_partial_credit(self):
            self.weight = 10
            self.score = 5
            self.assertTrue(False, "Didn't quite make it.")
            self.score = self.score + 5
            return

        @weight(10)
        @leaderboard('fastest fail')
        def test_failure_leaderboard(self, set_leaderboard_score=None):
            """ Testing something that fails. """
            set_leaderboard_score(100)
            self.assertTrue(False)
            return

        @visibility('after_due_date')
        def test_failure(self):
            print("Some output.")
            self.weight = 10
            self.assertFalse(True)
            return

        def test_error(self):
            self.weight = 10
            raise SyntaxError

    def test_json_successful(self):
        suite = unittest.TestLoader().loadTestsFromTestCase(self.TestPassing)
        results = GradedRunner().run(suite)
        results = json.loads(results.json)

        self.assertIn('tests', results)
        self.assertEqual(5, len(results['tests']))
        self.assertEqual(15, sum([test['score'] for test in results['tests']]))
        self.assertTrue(all(['output' in test for test in results['tests']]))

        self.assertIn('leaderboard', results)
        self.assertEqual(2, len(results['leaderboard']))

        self.assertIn('visibility', results)
        self.assertEqual(len([t for t in results['tests'] if 'visibility' in t]), 1)

        self.assertIn('execution_time', results)

        self.assertIsInstance(results['tests'][0]['output'], str)
        return

    def test_markdown_successful(self):
        suite = unittest.TestLoader().loadTestsFromTestCase(self.TestPassing)
        results = GradedRunner().run(suite)
        results = results.markdown
        self.assertIsInstance(results, str)
        return

    class TestFailing(ScoringMixin, unittest.TestCase):

        def setUp(self):
            self.require('thingsthatshallnotbe')
            return super().setUp()

        @weight(10)
        def test_something(self):
            self.assertTrue(True)

    def test_json_failing(self):
        suite = unittest.TestLoader().loadTestsFromTestCase(self.TestFailing)
        results = GradedRunner().run(suite)
        results = json.loads(results.json)

        self.assertIn('tests', results)
        self.assertEqual(1, len(results['tests']))

        self.assertIn('leaderboard', results)
        self.assertEqual(0, len(results['leaderboard']))

        self.assertIn('visibility', results)

        self.assertIn('execution_time', results)
        return


class TestClassSetupFails(unittest.TestCase):
    class Test(ScoringMixin, unittest.TestCase):

        @classmethod
        def setUpClass(cls):
            assert False

        def test_true(self):
            self.weight = 10
            self.assertTrue(True)

    def test_results(self):
        suite = unittest.TestLoader().loadTestsFromTestCase(self.Test)
        results = GradedRunner().run(suite)
        results = json.loads(results.json)

        self.assertEqual(len(results['tests']), 1)
        self.assertIsInstance(results['tests'][0]['output'], str)
        self.assertNotEqual(results['tests'][0]['output'], '')
