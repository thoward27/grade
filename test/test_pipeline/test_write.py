import os
import unittest

from grade.pipeline import *


class TestWrite(unittest.TestCase):
    """ Testing commands that write output. """

    def test_stdout(self):
        results = Run(['echo', 'hello'])()
        results = WriteStdout()(results)

        with self.assertRaises(FileExistsError):
            WriteStdout(overwrite=False)(results)

        self.assertIsInstance(results, CompletedProcess)
        with open('temp', 'r') as f:
            self.assertEqual(results.stdout, f.read())
        os.remove('temp')
        return

    def test_stderr(self):
        results = Run('>&2 echo error', shell=True)()
        results = WriteStderr()(results)

        with self.assertRaises(FileExistsError):
            WriteStderr(overwrite=False)(results)

        self.assertIsInstance(results, CompletedProcess)
        with open('temp', 'r') as f:
            self.assertEqual(results.stderr, f.read())
        os.remove('temp')
        return

    def test_outputs(self):
        results = Run(['ls'])()
        WriteOutputs('temp')(results)

        with open('temp.stdout', 'r') as f:
            self.assertEqual(results.stdout, f.read())
        os.remove('temp.stdout')

        with open('temp.stderr', 'r') as f:
            self.assertEqual(results.stderr, f.read())
        os.remove('temp.stderr')
        return
