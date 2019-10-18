""" Tests for the runners module.
"""

import unittest

from grade.runners import *


class TestJSON(unittest.TestCase):

    class Test(unittest.TestCase):
        def test_something(self):
            self.assertTrue(True)
            return

    def test_run(self):
        suite = unittest.TestLoader().loadTestsFromTestCase(self.Test)
        results = JSONRunner().run(suite).save()
        return


class TestMD(unittest.TestCase):

    class Test(unittest.TestCase):
        def test_something(self):
            self.assertTrue(True)
            return

    def test_output(self):
        suite = unittest.TestLoader().loadTestsFromTestCase(self.Test)
        results = unittest.TextTestRunner().run(suite)
        return
