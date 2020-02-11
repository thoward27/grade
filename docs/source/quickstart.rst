================================
Quick Start Guide
================================

By the end of this document you should be able to

1. Use the Pipeline
2. Assign unit tests a weight
3. Give partial credit
4. Establish a leaderboard

Given the following code (from RosettaCode):

.. code:: python3

    def encode(input_string):
        count = 1
        prev = ''
        lst = []
        for character in input_string:
            if character != prev:
                if prev:
                    entry = (prev,count)
                    lst.append(entry)
                    #print lst
                count = 1
                prev = character
            else:
                count += 1
        else:
            try:
                entry = (character,count)
                lst.append(entry)
                return (lst, 0)
            except Exception as e:
                print("Exception encountered {e}".format(e=e))
                return (e, 1)

    def decode(lst):
        q = ""
        for character, count in lst:
            q += character * count
        return q

    if __name__ == "__main__":
        s = input()
        print(decode(encode(s)))

Traditional unit testing would have some trouble with testing the `main`
portion of the code. With Grade, we can write a testing suite as follows:

.. code:: python3

    import unittest

    from grade.pipeline import *
    from grade.mixins import ScoringMixin

    class Tests(ScoringMixin, unittest.TestCase):

        @classmethod
        def setUpClass(cls):
            """ Any failures here prevent a student from accruing any points. """
            self.require('studentscode.py')

        def test_encode_decode(self):
            """ A typical unit test for the encode / decode functions. """
            from studentscode import encode, decode

            self.weight = 10

            # Plain assertions make the test a pass / fail.
            self.assertEqual(decode(encode('hello')), 'hello')

            # You can also assign partial credit.
            self.score = string_distance(decode(encode('hello')), 'hello')

        def test_main(self):
            """ Testing script execution. """
            self.weight = 10

            # To test executable files, just build a pipeline!
            Pipeline(
                Run(['python', 'studentcode.py'], input='hello')
                AssertExitSuccess(),
                AssertStdoutMatches('hello'),
            )() # It a students' code passes all of the tests, they get full credit.

To execute this ``TestCase``, simply run ``python -m grade run``
from the root directory where both files are contained.

Once you have run a given test suite, you can control output from the CLI.
Simply run ``python -m grade report`` to have the output written to ``stdout``.
For example, to output to Markdown: ``python -m grade report markdown``.

Further Reading
=====================

Within the Github Repository for this project you will find a file
`example.py`, which contains a more thorough example.
