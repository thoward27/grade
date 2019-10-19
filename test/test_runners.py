""" Tests for the runners module.
"""

import unittest

from grade.runners import *


class TestJSON(unittest.TestCase):

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

    class Test(unittest.TestCase):

        def test_something(self):
            """ Testing one thing or another. """
            self.assertTrue(True)
            return

        def test_successfully_something_else(self):
            self.assertFalse(False)
            return

        def test_failure(self):
            """ Testing something that fails. """
            self.assertTrue(False)
            return

        def test_failure2(self):
            self.assertFalse(True)
            return

        def test_error(self):
            raise SyntaxError

    def test_run(self):
        suite = unittest.TestLoader().loadTestsFromTestCase(self.Test)
        results = JSONRunner().run(suite)
        print(json.dumps(results.data, indent=4))
        self.assertDictEqual(
            {
                'tests': [
                    {
                      'name': 'test_something: Testing one thing or another',
                      'score': 0,
                      'max_score': 0
                    },
                    {
                        'name': 'test_successfully_something_else',
                        'score': 0,
                        'max_score': 0,
                    },
                    {
                        'name': 'test_failure',
                        'score': 0,
                        'max_score': 0,
                        'output': 'FAILURE'
                    }
                ],
                'visibility': 'visible',
                'execution_time': results.data['execution_time'],
                'score': 0,
            },
            results.data
        )
        return


class TestMD(unittest.TestCase):

    class Test(unittest.TestCase):
        def test_something(self):
            self.assertTrue(True)
            return

    @unittest.skip
    def test_output(self):
        suite = unittest.TestLoader().loadTestsFromTestCase(self.Test)
        results = unittest.TextTestRunner().run(suite)
        return
