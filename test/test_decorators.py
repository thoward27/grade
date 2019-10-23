""" Tests for the decorators module.
"""

import unittest

from grade.decorators import *


class TestDecorators(unittest.TestCase):

    def test_weight(self):
        """ Can weights be set? """

        @weight(10)
        def test_something():
            return

        self.assertEqual(test_something.__weight__, 10)
        return

    def test_visibility(self):
        """ Can visibility be set? """

        def test_default():
            return

        # There should be nothing set here.
        with self.assertRaises(AttributeError):
            getattr(test_default, '__visibility__')  # test_default.__visibility__

        @visibility('hidden')
        def test_hidden():
            return

        self.assertEqual(test_hidden.__visibility__, 'hidden')

        @visibility('after_due_date')
        def test_after_due_date():
            return

        self.assertEqual(test_after_due_date.__visibility__, 'after_due_date')

        @visibility('visible')
        def test_visible():
            return

        self.assertEqual(test_visible.__visibility__, 'visible')
        return

    def test_leaderboard(self):
        @leaderboard()
        def test_defaults():
            return

        self.assertEqual(test_defaults.__leaderboard_title__, 'test_defaults')
        self.assertEqual(test_defaults.__leaderboard_order__, 'desc')
        self.assertEqual(test_defaults.__leaderboard_score__, None)

        @leaderboard('title')
        def test_title(set_leaderboard_score=None):
            set_leaderboard_score(10)
            return

        test_title()

        self.assertEqual(test_title.__leaderboard_title__, 'title')
        self.assertEqual(test_title.__leaderboard_score__, 10)

        @leaderboard('title2', 'asc')
        def test_title_and_order(set_leaderboard_score=None):
            set_leaderboard_score('A')
            return

        test_title_and_order()

        self.assertEqual(test_title_and_order.__leaderboard_title__, 'title2')
        self.assertEqual(test_title_and_order.__leaderboard_order__, 'asc')
        self.assertEqual(test_title_and_order.__leaderboard_score__, 'A')
        return
