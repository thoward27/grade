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
            self.weight = 10
            self.assertFalse(True)
            return

        def test_error(self):
            self.weight = 10
            raise SyntaxError

    def test_run(self):
        suite = unittest.TestLoader().loadTestsFromTestCase(self.Test)
        results = GradedRunner().run(suite)
        self.assertDictEqual(
            {
                "tests": [
                    {
                        "name": "test_error",
                        "max_score": 10,
                        "score": 0,
                        "output": "Traceback (most recent call last):\n  File \"/mnt/c/Users/thowa/Github/grade/test/test_runners.py\", line 78, in test_error\n    raise SyntaxError\n  File \"<string>\", line None\nSyntaxError: <no detail available>\n"
                    },
                    {
                        "name": "test_failure",
                        "max_score": 10,
                        "score": 0,
                        "output": "Traceback (most recent call last):\n  File \"/mnt/c/Users/thowa/Github/grade/test/test_runners.py\", line 73, in test_failure\n    self.assertFalse(True)\nAssertionError: True is not false\n"
                    },
                    {
                        "name": "test_failure_leaderboard: Testing something that fails.",
                        "max_score": 10,
                        "score": 0,
                        "output": "Traceback (most recent call last):\n  File \"/mnt/c/Users/thowa/Github/grade/grade/decorators.py\", line 81, in wrapper\n    return func(*args, **kwargs)\n  File \"/mnt/c/Users/thowa/Github/grade/test/test_runners.py\", line 68, in test_failure_leaderboard\n    self.assertTrue(False)\nAssertionError: False is not true\n"
                    },
                    {
                        "name": "test_full_credit: Testing one thing or another.",
                        "max_score": 10,
                        "score": 10
                    },
                    {
                        "name": "test_partial_credit",
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
                "execution_time": results.json['execution_time'] # Since this varies!
            },
            results.json
        )
        return
