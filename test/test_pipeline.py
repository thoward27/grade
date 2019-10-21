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

        results = Run('echo hello', shell=True)()
        AssertValgrindSuccess()(results)
        return

    def test_stdout_matches(self):
        # Specifying stdout.
        results = Run(['echo', 'hello_world'])()
        results = AssertStdoutMatches('hello_world')(results)
        self.assertIsInstance(results, CompletedProcess)
        
        # Inferring stdout.
        results = WriteStdout('hello_world.stdout')(results)
        results = AssertStdoutMatches()(results)
        self.assertIsInstance(results, CompletedProcess)
        os.remove('hello_world.stdout')
        
        # Cannot infer file of shell=True commands.
        with self.assertRaises(ValueError):
            AssertStdoutMatches()(Run('echo hello world', shell=True)())
        return

    def test_stderr_matches(self):
        results = Run('>&2 echo hello_world', shell=True)()
        results = AssertStderrMatches('hello_world')(results)
        self.assertIsInstance(results, CompletedProcess)

        results = WriteStderr('hello_world.stderr')(results)
        with self.assertRaises(ValueError):
            results = AssertStderrMatches()(results)
        self.assertIsInstance(results, CompletedProcess)
        
        os.remove('hello_world.stderr')
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
        results = WriteStdout()(results)
        self.assertIsInstance(results, CompletedProcess)
        with open('temp', 'r') as f:
            self.assertEqual(results.stdout, f.read())
        os.remove('temp')
        return

    def test_stderr(self):
        results = Run('>&2 echo error', shell=True)()
        results = WriteStderr()(results)
        self.assertIsInstance(results, CompletedProcess)
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

class TestLambda(unittest.TestCase):

    def test_improper_return(self):
        """ Lambda must return results. """
        results = Run(['ls'])()
        with self.assertRaises(TypeError):
            results = Lambda(lambda results: True)(results)
        return

    def test_proper_return(self):
        """ Lambda that does return completedprocess. """
        results = Run(['ls'])()
        results = Lambda(lambda results: results)(results)
        self.assertIsInstance(results, CompletedProcess)
        return

    def randomFunction(self, results):
        """ Function for the test below. """
        return results

    def test_passing_function(self):
        """ Lambda that executes a function. """
        results = Run(['ls'])()
        results = Lambda(self.randomFunction)(results)
        self.assertIsInstance(results, CompletedProcess)
        return
