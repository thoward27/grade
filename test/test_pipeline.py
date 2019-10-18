""" Tests for the pipeline module.
"""

import os
import unittest

from grade.pipeline import *


class TestPipeline(unittest.TestCase):

    def test_fails(self):
        with self.assertRaises(AssertionError):
            Pipeline(
                Run(['ls']),
                AssertExitFailure()
            )()

    def test_fail_multiple(self):
        with self.assertRaises(AssertionError):
            tests = map(lambda t: Pipeline(Run(['ls']), AssertExitFailure()), range(10))
            [test() for test in tests]

    def test_passes(self):
        Pipeline(
            Run(['ls']),
            AssertExitSuccess()
        )
        return

    def test_pass_multiple(self):
        tests = map(lambda t: Pipeline(Run(['ls']), AssertExitSuccess()), range(10))
        [test() for test in tests]


class TestPartialCredit(unittest.TestCase):

    def test_full_credit(self):
        pipelines = map(lambda t: Pipeline(Run(['ls'])), range(10))
        results = PartialCredit(pipelines, 10)()
        self.assertEqual(results.score, 10)
        return

    def test_partial_credit(self):
        pipelines = map(lambda t: Pipeline(Run([t]), AssertExitSuccess()), ['ls', 'void'])
        with self.assertLogs() as logs:
            results = PartialCredit(pipelines, 10)()
        self.assertIn("ERROR:root:[Errno 2] No such file or directory: 'void'", logs.output)
        self.assertEqual(results.score, 5)
        return

    def test_no_credit(self):
        pipelines = map(lambda t: Pipeline(Run(['ls']), AssertExitFailure()), range(10))
        with self.assertLogs() as logs:
            results = PartialCredit(pipelines, 10)()
        self.assertIn("ERROR:root:['ls'] exited successfully.", logs.output)
        self.assertEqual(results.score, 0)
        return


class TestAsserts(unittest.TestCase):

    def test_exit_success(self):
        results = Run(['ls'])()
        AssertExitSuccess()(results)
        return

    def test_exit_failure(self):
        results = Run(['ls', '--iamnotanarg'])()
        AssertExitFailure()(results)
        return

    def test_valgrind(self):
        results = Run(['ls'])()
        AssertValgrindSuccess()(results)
        return

    def test_stdout_matches(self):
        results = Run(['echo', 'hello world'])()
        AssertStdoutMatches()(results, 'hello world')
        return

    def test_stderr_matches(self):
        results = Run('>&2 echo hello world', shell=True)()
        AssertStderrMatches()(results, 'hello world')
        return


class TestRun(unittest.TestCase):

    def test_valid_program(self):
        results = Run(['ls'])()
        self.assertEqual(results.returncode, 0)
        return

    def test_nonexistant(self):
        with self.assertRaises(FileNotFoundError):
            Run(['idonotexist'])()
        return

    def test_shell_command(self):
        results = Run('echo test | grep test', shell=True)()
        self.assertEqual(results.returncode, 0)
        return

    def test_timeout(self):
        import subprocess
        with self.assertRaises(subprocess.TimeoutExpired):
            Run(['sleep', '30'], timeout=1)()
        return


class TestWrite(unittest.TestCase):
    """ Testing commands that write output. """

    def test_stdout(self):
        results = Run(['echo', 'hello'])()
        WriteStdout()(results)
        with open('temp', 'r') as f:
            self.assertEqual(results.stdout, f.read())
        os.remove('temp')
        return

    def test_stderr(self):
        results = Run('>&2 echo error', shell=True)()
        WriteStderr()(results)
        with open('temp', 'r') as f:
            self.assertEqual(results.stderr, f.read())
        os.remove('temp')
        return

    def test_outputs(self):
        results = Run(['ls'])()
        WriteOutputs()(results, 'temp')

        with open('temp.stdout', 'r') as f:
            self.assertEqual(results.stdout, f.read())
        os.remove('temp.stdout')

        with open('temp.stderr', 'r') as f:
            self.assertEqual(results.stderr, f.read())
        os.remove('temp.stderr')
        return
