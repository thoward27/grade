""" Tests for the pipeline module.
"""

import os
import unittest
import shutil

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

    def test_iteration(self):
        pipeline = Pipeline(
            Run(['ls']),
            AssertExitSuccess(),
            AssertValgrindSuccess(),
            WriteOutputs('temp'),
        )
        [self.assertTrue(callable(callback)) for callback in pipeline]
        self.assertIsInstance(pipeline[1], AssertExitSuccess)
        self.assertEqual(len(pipeline), 4)
        return


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
        self.assertIn("ERROR:root:[Errno 2] No such file or directory: 'void'", logs.output[0])
        self.assertEqual(results.score, 5)
        return

    def test_no_credit(self):
        pipelines = map(lambda t: Pipeline(Run(['ls']), AssertExitFailure()), range(10))
        with self.assertLogs() as logs:
            results = PartialCredit(pipelines, 10)()
        self.assertEqual(10, len(logs.output))
        self.assertIn("ERROR:root:['ls'] should have exited unsuccessfully.", logs.output)
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

    @unittest.skipIf(shutil.which('valgrind') is None, 'Need valgrind.')
    def test_valgrind(self):
        results = Run(['ls'])()
        AssertValgrindSuccess()(results)

        results = Run('echo hello', shell=True)()
        AssertValgrindSuccess()(results)

        results = Run('grep pip < README.md', shell=True)()
        AssertValgrindSuccess()(results)
        return

class TestAssertStdoutMatches(unittest.TestCase):

    def test_stdout_no_match(self):
        """ What happens when stdout does not match? """
        results = Run(['echo', 'hello_world'])()
        with self.assertRaises(AssertionError):
            AssertStdoutMatches('goodbye_world')(results)
        return

    def test_stdout_matches(self):
        """ What if stdout does match? """
        results = Run(['echo', 'hello_world'])()
        results = AssertStdoutMatches('hello_world')(results)
        self.assertIsInstance(results, CompletedProcess)
        return

    def test_inferring_filename(self):
        """ Can we infer filename if conventions are followed? """
        results = Run(['echo', 'hello_world'])()
        results = WriteOutputs('hello_world')(results)
        results = AssertStdoutMatches()(results)
        self.assertIsInstance(results, CompletedProcess)
        os.remove('hello_world.stdout')
        os.remove('hello_world.stderr')
        return

    def test_cannot_infer_filename(self):
        """ What if there is no file to infer from? """
        with self.assertRaises(ValueError):
            AssertStdoutMatches()(Run('echo hello world', shell=True)())

        results = Run(['echo', 'hello world'])()
        with self.assertRaises(AssertionError):
            AssertStdoutMatches()(results)
        return

    def test_cannot_infer_shell(self):
        """ Should not be able to infer filenames when shell=True """
        results = Run('echo hello_world', shell=True)()
        with self.assertRaises(ValueError):
            AssertStdoutMatches()(results)

    def test_passing_both(self):
        results = Run(['echo', 'hello'])()
        with self.assertRaises(ValueError):
            AssertStdoutMatches('hello', 'world')(results)
        return

    def test_passing_filename(self):
        results = Run(['echo', 'hello'])()
        with open('hello.stdout', 'w') as f:
            f.write('hello')
        AssertStdoutMatches(filepath='hello.stdout')(results)
        os.remove('hello.stdout')
        return

class TestAssertStderrMatches(unittest.TestCase):

    def test_stderr_no_match(self):
        """ What happens when stderr does not match? """
        results = Run('>&2 echo hello_world', shell=True)()
        with self.assertRaises(AssertionError):
            AssertStderrMatches('goodbye_world')(results)
        return

    def test_stderr_matches(self):
        """ What if stderr does match? """
        results = Run('>&2 echo hello_world', shell=True)()
        results = AssertStderrMatches('hello_world')(results)
        self.assertIsInstance(results, CompletedProcess)
    
    def test_inferring_filename(self):
        """ Can we infer filename if conventions are followed? """
        results = Run(['grep', '-h'])()
        results = WriteOutputs('-h')(results)
        results = AssertStderrMatches()(results)
        self.assertIsInstance(results, CompletedProcess)
        os.remove('-h.stdout')
        os.remove('-h.stderr')
    
    def test_cannot_infer_filename(self):
        """ What if there is no file to infer from? """
        results = Run(['grep', '-h'])()
        with self.assertRaises(AssertionError):
            AssertStderrMatches()(results)
        return

    def test_cannot_infer_shell(self):
        """ Should not be able to infer filename when shell=True """
        results = Run('>&2 echo hello_world', shell=True)()
        with self.assertRaises(ValueError):
            AssertStderrMatches()(results)
        return

    def test_passing_both(self):
        results = Run('>&2 echo hello', shell=True)()
        with self.assertRaises(ValueError):
            AssertStderrMatches('hello', 'world')(results)
        return

    def test_passing_filename(self):
        results = Run('>&2 echo hello', shell=True)()
        with open('hello.stderr', 'w') as f:
            f.write('hello')
        AssertStderrMatches(filepath='hello.stderr')(results)
        os.remove('hello.stderr')
        return
        

class TestAssertRegex(unittest.TestCase):
    def test_regex_stdout(self):
        results = Run(['cat', 'README.md'])()
        results = AssertRegexStdout(r'python')(results)
        self.assertIsInstance(results, CompletedProcess)
        with self.assertRaises(AssertionError) as e:
            AssertRegexStdout(r'idontthinkthisshouldbehere')(results)
        return

    def test_regex_stderr(self):
        results = Run('>&2 echo hello_world', shell=True)()
        results = AssertRegexStderr(r'hello')(results)
        self.assertIsInstance(results, CompletedProcess)
        with self.assertRaises(AssertionError):
            AssertRegexStderr(f'bah humbug')(results)
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
        with self.assertRaises(TimeoutError):
            Run(['sleep', '30'], timeout=1)()
        return

    def test_input(self):
        Pipeline(
            Run(['cat', 'README.md']),
            AssertExitSuccess(),
            Run(['grep', 'Setup'], input=lambda r: r.stdout),
            AssertStdoutMatches('## Setup')
        )()
        Pipeline(
            Run(['grep', 'hello', '-'], input="hello world\nhear me test things!"),
            AssertStdoutMatches('hello world')
        )()
        Pipeline(
            Run(['python', '-c', 'x = input(); print(x)'], input='5'),
            AssertStdoutMatches('5')
        )()


class TestCheck(unittest.TestCase):
    """ Tests the Check command. """
    def test_check_successful(self):
        """ Check should not change a successful execution by asserting exit success. """
        results = Run(['ls'])()
        results = Check(AssertExitSuccess())(results)
        self.assertEqual(results.returncode, 0)
        return

    def test_check_failure(self):
        """ Check should set results to successful by asserting exit failure. """
        results = Run(['grep', '--asdfghjk'])()
        results = Check(AssertExitFailure())(results)
        self.assertEqual(results.returncode, 0)
        return

    def test_check_successful_failure(self):
        """ Checks a failure for success. """
        results = Run(['grep', '--notanarg'])()
        results = Check(AssertExitSuccess())(results)
        self.assertNotEqual(results.returncode, 0)
        return


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


class TestLambda(unittest.TestCase):

    def test_simple(self):
        """ Lambda that does return completedprocess. """
        results = Run(['ls'])()
        results = Lambda(lambda r: r)(results)
        self.assertIsInstance(results, CompletedProcess)
        return

    @staticmethod
    def randomFunction(results):
        """ Function for the test below. """
        return results

    def test_passing_function(self):
        """ Lambda that executes a function. """
        results = Run(['ls'])()
        results = Lambda(self.randomFunction)(results)
        self.assertIsInstance(results, CompletedProcess)
        return
