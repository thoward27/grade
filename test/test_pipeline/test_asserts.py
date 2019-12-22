import os
import shutil
import unittest

from grade.pipeline import *


class TestAsserts(unittest.TestCase):

    def test_exit_success(self):
        results = Run(['ls'])()
        AssertExitSuccess()(results)
        return

    def test_exit_failure(self):
        results = Run(['ls', '--iamnotanarg'])()
        AssertExitFailure()(results)
        return

    def test_assert_exit_status(self):
        Pipeline(
            Run(['echo', 'hello world']),
            AssertExitStatus(0),
            Not(AssertExitStatus(1)),
        )()
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

    def test_not(self):
        Pipeline(
            Run(['ls']),
            # Essentially, assert not contains, which should fail.
            Not(AssertStdoutContains(strings=['imaginary.file']))
        )()
        with self.assertRaises(AssertionError):
            Pipeline(
                Run(['echo', 'hello world']),
                Not(AssertStdoutContains(strings=['hello']))
            )()
        return

    def test_or(self):
        Pipeline(
            Run(['echo', 'hello world']),
            Or(
                AssertStdoutContains(['goodbye']),
                AssertStdoutContains(['hello'])),
        )()
        with self.assertRaises(AssertionError):
            Pipeline(
                Run(['echo', 'hello world']),
                Or(
                    AssertStdoutContains(['goodbye']),
                    AssertStderrContains(['goodbye'])
                )
            )()
        return

    def test_faster(self):
        Pipeline(
            Run(['echo', 'hello world']),
            AssertFaster(10),
            Not(AssertFaster(0)),
        )()
        return


class TestAssertContains(unittest.TestCase):
    def test_stdout_contains(self):
        results = Run(['ls'])()
        AssertStdoutContains(['README.md', 'setup.py'])(results)

        with self.assertRaises(AssertionError):
            AssertStdoutContains(['pickleRick'])(results)

    def test_stderr_contains(self):
        results = Run('>&2 echo hello', shell=True)()
        AssertStderrContains(['hello'])(results)

        with self.assertRaises(AssertionError):
            AssertStderrContains(['world'])(results)


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
        results = AssertStdoutRegex(r'python')(results)
        self.assertIsInstance(results, CompletedProcess)
        with self.assertRaises(AssertionError) as e:
            AssertStdoutRegex(r'idontthinkthisshouldbehere')(results)
        return

    def test_regex_stderr(self):
        results = Run('>&2 echo hello_world', shell=True)()
        results = AssertStderrRegex(r'hello')(results)
        self.assertIsInstance(results, CompletedProcess)
        with self.assertRaises(AssertionError):
            AssertStderrRegex(f'bah humbug')(results)
        return


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
