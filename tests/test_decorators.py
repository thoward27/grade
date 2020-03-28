""" Tests for the decorators module.
"""

import unittest

from grade.decorators import (
    weight,
    visibility,
    leaderboard,
)


class TestDecorators(unittest.TestCase):
    def test_weight(self):
        """ Can weights be set? """

        @weight(10)
        def test_something():
            pass

        self.assertEqual(test_something._g_weight, 10)

    def test_visibility(self):
        """ Can visibility be set? """

        def test_default():
            pass

        # There should be nothing set here.
        with self.assertRaises(AttributeError):
            getattr(test_default, "_g_visibility")  # test_default._g_visibility

        @visibility("hidden")
        def test_hidden():
            pass

        self.assertEqual(test_hidden._g_visibility, "hidden")

        @visibility("after_due_date")
        def test_after_due_date():
            pass

        self.assertEqual(test_after_due_date._g_visibility, "after_due_date")

        @visibility("visible")
        def test_visible():
            pass

        self.assertEqual(test_visible._g_visibility, "visible")

    def test_leaderboard(self):
        @leaderboard()
        def test_defaults():
            pass

        self.assertEqual(test_defaults._g_leaderboard_title, "test_defaults")
        self.assertEqual(test_defaults._g_leaderboard_order, "desc")
        self.assertEqual(test_defaults._g_leaderboard_score, None)

        @leaderboard("title")
        def test_title(set_leaderboard_score=None):
            set_leaderboard_score(10)

        test_title()

        self.assertEqual(test_title._g_leaderboard_title, "title")
        self.assertEqual(test_title._g_leaderboard_score, 10)

        @leaderboard("title2", "asc")
        def test_title_and_order(set_leaderboard_score=None):
            set_leaderboard_score("A")

        test_title_and_order()

        self.assertEqual(test_title_and_order._g_leaderboard_title, "title2")
        self.assertEqual(test_title_and_order._g_leaderboard_order, "asc")
        self.assertEqual(test_title_and_order._g_leaderboard_score, "A")
