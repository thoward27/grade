""" Grade Example Flow.
"""
import os
import unittest

from grade import pipeline, mixins, decorators, runners
from grade.pipeline import Pipeline, Run, AssertExitSuccess, PartialCredit, AssertValgrindSuccess


def student_function(x: list, m: int) -> list:
    """ Random student function. """
    return sum(x) % m

class Tests(mixins.ScoringMixin, unittest.TestCase):
    """ An example TestCase, with the ScoringMixing.
    
    Grade requires a TestCase as a starting point, from there,
    we can give each testcase a weight, assign partial credit, 
    and much more!
    """

    @classmethod
    def setUpClass(cls):
        """ Assert that we have everything we need to run the tests.

        Here, we will compile any code that must be compiled, along
        with checking for all files that *must* exist for a student
        to collect any points.

        If anything in this block fails, the student should receive a 0.
        """
        # Compilation
        compile = pipeline.Run(['ls'])()
        assert(compile.returncode == 0)

        # Requiring files.
        cls.require('example.py')
        return


    def test_compile(self):
        """ Test working compilation.

        At this point, we know that the code compiled and all files were
        present, so we can just assertTrue(True)!
        """
        self.weight = 1  # Set the weight of the unit test (max score)
        self.assertTrue(True)
        return

    # For most grading functions, we provide both methods and decorators.
    # There is no functional difference between methods and decorators.

    @decorators.weight(10) # Equivalent to self.weight = 10
    def test_student_function(self):
        """ Test the students python code on some inputs.
        """
        self.assertEqual(
            student_function(list(range(10)), 5),
            sum(list(range(10))) % 5
        )

        # If making it this far into the test represents some key milestone
        # you can assign the student some partial credit. If score is never
        # set, it defaults to weight if the test is successful, 0 otherwise.
        self.score = self.score + 5

        # As soon as you assign a student partial credit, score is locked to
        # that value. Remember to update it before the test exits!

        self.assertEqual(student_function([0], 1), 0)

        # Since the student made it to the end and we set a partial score,
        # we must finish the test by setting their score to full credit.
        self.score = self.weight
        return

    # Grade executable files.

    @decorators.weight(10)
    def test_executable(self):
        """ Checking executable files with a Pipeline.

        Pipelines are designed around testing executable files.
        They are comprised of "layers" which pass subprocess.CompletedProcess
        objects to each other. You can stack layers however you'd like,
        but they must start with a call to Run(), which generates the initial
        CompletedProcess.
        """
        Pipeline(
            Run(['ls']),
            AssertExitSuccess(),
            AssertValgrindSuccess()
        )()
        return

    def test_executable_two(self):
        """ Checking multiple runs of an executable.

        We can also use pipelines in comprehensions and maps,
        to test multiple targets at once.

        Say you wanted to test that a students code returns zero
        for all valid test inputs; this would be a perfect usecase for
        multiple targets.
        """
        self.weight = 10

        # noinspection PyShadowingNames
        def pipeline(testcase):
            """ Create a pipeline for the given testcase. """
            return Pipeline(
                Run(['echo', testcase]),
                AssertExitSuccess()
            )

        # Now make an iterable (ex: list[str], glob, etc.)
        testcases = [c for c in 'hello world']

        # You can execute them all at once (all or nothing credit)
        [pipeline(testcase)() for testcase in testcases]

        # Or, you can also award partial credit for each testcase:
        results = PartialCredit(map(pipeline, testcases), 10)()
        self.score = results.score
        return

    # Any output written to stdout or stderr is captured and included
    # in the tests' output value.
    def test_failure(self):
        print("False is not True!")
        self.assertTrue(False)


if __name__ == '__main__':
    # You can run things from inside of a script as follows:
    suite = unittest.TestLoader().discover('./', pattern='example.py')
    results = runners.GradedRunner().run(suite)
    print(results.json)

    # Or, you can use the command line interface:
    # `python -m grade -h` to get started with the CLI.
