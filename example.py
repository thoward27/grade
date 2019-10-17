import sys
sys.setrecursionlimit(500)

import os
import unittest
from grade import pipeline, mixins, decorators
from grade.pipeline import Pipeline, Run, AssertExitSuccess, PartialCredit, AssertValgrindSuccess


def student_function(x: list, m: int) -> list:
    return sum(x) % m


class Tests(mixins.ScoringMixin, unittest.TestCase):

    # First, override the setUpClass method to prevent any test
    # case from running in invalid conditions.

    @classmethod
    def setUpClass(cls):
        """ Assert that everything is present.
        """
        # Check compilation of code.
        compile = pipeline.Run(['ls'])()
        assert(compile.returncode == 0)

        # Check for file existence.
        if not os.path.exists('example.py'):
            # Provide a more descriptive exception.
            raise AssertionError('Important thing <x> is missing.')
        return

    # If you want to test for software compilation, at this point,
    # you can just assertTrue(True), since setUpClass already
    # checked that everything you need is there.
    def test_compile(self):
        """ Test working compilation.
        """
        self.weight = 1  # Set the weight of the unit test
        self.assertTrue(True)
        return

    # For most grading functions, we provide both method-format,
    # and decorator format.

    @decorators.weight(1)  # Equivalent to self.weight() method.
    def test_compile_decorated(self):
        """ Test working compilation, with decorator for weight.
        """
        self.assertTrue(True)
        return

    # In general, you can always choose between decorators, or
    # using the builtin methods.

    # Note: method versions may run slightly slower than the decorators.

    # Grade student functions.

    def test_student_function(self):
        """ Test the students python code on some inputs.
        """
        self.weight = 10
        self.assertEqual(
            student_function(list(range(10)), 5),
            sum(list(range(10))) % 5
        )

        # And feel free to use partial credit!
        self.score = self.score + 5

        # But if you do use the score method,
        # a student will get the full amount of points you add.
        # Say, we only want to check one more condition,

        self.assertEqual(student_function([0], 1), 0)

        # Now, we can just set score to weight.

        self.score = self.weight
        return

    # Grade executable files.

    @decorators.weight(10)
    def test_executable(self):
        """ Checking executables with Pipelines.
        """
        Pipeline(
            Run(['ls']),
            AssertExitSuccess(),
            AssertValgrindSuccess()
        )()
        return

    # Yes, it's that easy!
    # Pipeline is used to handle executable programs only,
    # and it relies on the Run() command being first. It
    # passes subprocess.results forward through the rest of
    # the commands in the Pipeline.

    # You can also grade on multiple targets.

    def test_executable_two(self):
        """ Checking multiple runs of an executable.
        """
        self.weight = 10

        def pipeline(testcase):
            return Pipeline(
                Run(['echo', testcase]),
                AssertExitSuccess()
            )

        # Now make an iterable (list[str], glob, etc)
        testcases = [c for c in 'hello world']

        # You can execute them all at once (all or nothing)
        results = [pipeline(testcase)() for testcase in testcases]

        # We can also award partial credit
        results = PartialCredit(map(pipeline, testcases), 10)()
        self.score = results.score
        return


if __name__ == '__main__':
    import unittest
    
    suite = unittest.TestLoader().discover('./', pattern='example.py')
    unittest.TextTestRunner(
        stream=sys.stdout,
        descriptions=True,
        verbosity=1
    ).run(suite)
