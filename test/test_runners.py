""" Tests for the runners module.
"""

import unittest

from grade.runners import *
from grade.mixins import *
from grade.decorators import *


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

    class Test(ScoringMixin, unittest.TestCase):

        @weight(10)
        def test_full_credit(self):
            """ Testing one thing or another. """
            self.leaderboardTitle = 'Successful'
            self.leaderboardOrder = 'asc'
            self.leaderboardScore = 10

            self.assertTrue(True)
            return

        def test_partial_credit(self):
            self.weight = 10
            self.score = 5
            self.assertFalse(False)
            return

        @weight(10)
        @leaderboard('fastest fail')
        def test_failure_leaderboard(self, set_leaderboard_score=None):
            """ Testing something that fails. """
            set_leaderboard_score(100)
            self.assertTrue(False)
            return

        def test_failure(self):
            print("Some output.")
            self.weight = 10
            self.assertFalse(True)
            return

        def test_error(self):
            self.weight = 10
            raise SyntaxError

    def test_json(self):
        suite = unittest.TestLoader().loadTestsFromTestCase(self.Test)
        results = GradedRunner().run(suite)
        self.maxDiff = None
        self.assertDictEqual(
            {
                "tests": [
                    {
                        "name": "TestRunner.Test.test_error",
                        "max_score": 10,
                        "score": 0,
                        "output": "test_runners.py, line 79, in test_error; raise SyntaxError; File \"<string>\", line None; SyntaxError: <no detail available>"
                    },
                    {
                        "name": "TestRunner.Test.test_failure",
                        "max_score": 10,
                        "score": 0,
                        "output": "test_runners.py, line 74, in test_failure; self.assertFalse(True); AssertionError: True is not false; Stdout:; Some output."
                    },
                    {
                        "name": "TestRunner.Test.test_failure_leaderboard: Testing something that fails.",
                        "max_score": 10,
                        "score": 0,
                        "output": "test_runners.py, line 68, in test_failure_leaderboard; self.assertTrue(False); AssertionError: False is not true"
                    },
                    {
                        "name": "TestRunner.Test.test_full_credit: Testing one thing or another.",
                        "max_score": 10,
                        "score": 10
                    },
                    {
                        "name": "TestRunner.Test.test_partial_credit",
                        "max_score": 10,
                        "score": 5
                    }
                ],
                "leaderboard": [
                    {
                        "name": "fastest fail",
                        "value": 100,
                        "order": "desc"
                    },
                    {
                        "name": "Successful",
                        "value": 10,
                        "order": "asc"
                    }
                ],
                "visibility": "visible",
                "execution_time": results.data['execution_time'] # Since this varies!
            },
            json.loads(results.json)
        )
        return
