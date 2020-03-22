import unittest

from grade.pipeline import (
    Run,
    Pipeline,
    AssertExitSuccess,
    AssertStdoutMatches,
)


class TestRun(unittest.TestCase):
    def test_valid_program(self):
        results = Run(["ls"])()
        self.assertEqual(results.returncode, 0)
        self.assertGreater(results.duration, 0)

    def test_nonexistant(self):
        with self.assertRaises(FileNotFoundError):
            Run(["idonotexist"])()

    def test_shell_command(self):
        results = Run("echo test | grep test", shell=True)()
        self.assertEqual(results.returncode, 0)
        self.assertGreater(results.duration, 0)

    def test_timeout(self):
        with self.assertRaises(TimeoutError):
            Run(["sleep", "30"], timeout=1)()

    @staticmethod
    def test_input():
        Pipeline(
            Run(["cat", "README.md"]),
            AssertExitSuccess(),
            Run(["grep", "Setup"], input=lambda r: r.stdout),
            AssertStdoutMatches("## Setup"),
        )()
        Pipeline(
            Run(["grep", "hello", "-"], input="hello world\nhear me test things!"),
            AssertStdoutMatches("hello world"),
        )()
        Pipeline(
            Run(["python", "-c", "x = input(); print(x)"], input="5"), AssertStdoutMatches("5")
        )()
