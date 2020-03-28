""" Mixins.
"""
import os
from glob import glob
from inspect import stack
from typing import List, Callable, Union, Tuple


class ScoringMixin:
    """ Provides scoring utility functions.
    """

    methods: List[tuple] = None

    def __str__(self) -> str:
        return type(self).__name__

    def getTests(self) -> List[Tuple[str, Callable]]:
        return [(key, getattr(self, key)) for key in dir(self) if key.startswith("test")]

    def getTest(self) -> Callable:
        """ Returns the topmost test method on the stack. """
        if not self.methods:
            self.methods = self.getTests()

        caller = [frame for frame in stack() if frame.function.startswith("test")][0]
        caller = [func for name, func in self.methods if name == caller.function][0]
        return caller

    def setattr(self, attribute, value) -> None:
        """ Updates the dictionary of the most recently called test method. """
        self.getTest().__dict__[attribute] = value

    # noinspection PyUnresolvedReferences
    @staticmethod
    def require(*files) -> None:
        """ Asserts all provided files exist.
        """
        assert files, "Nothing to require."
        for f in files:
            assert os.path.exists(f), f"{f} does not exist!"

    @staticmethod
    def find(pattern, recursive=True) -> List[str]:
        """ Returns all files matching pattern, case insensitive.
        """
        # Make it case insensitive
        pattern = "".join(p if not p.isalpha() else f"[{p.lower()}{p.upper()}]" for p in pattern)
        return glob(pattern, recursive=recursive)

    @property
    def weight(self) -> int:
        """ Returns the weight of the test. """
        return getattr(self.getTest(), "_g_weight", 0)

    @weight.setter
    def weight(self, weight: int) -> None:
        """ Sets the weight of the test. """
        self.setattr("_g_weight", weight)

    @property
    def score(self) -> Union[int, float]:
        """ Returns the current score for the test. """
        return getattr(self.getTest(), "_g_score", 0)

    @score.setter
    def score(self, score: Union[int, float]) -> None:
        """ Sets the score for the test. """
        self.setattr("_g_score", score)

    @property
    def visibility(self) -> str:
        """ Returns visibility of the test.

        This controls whether or not students should see the failing testcase.
        """
        return getattr(self.getTest(), "_g_visibility", "visible")

    @visibility.setter
    def visibility(self, visibility: str) -> None:
        """ Sets the visibility of the test. """
        self.setattr("_g_visibility", visibility)

    @property
    def leaderboard(self) -> dict:
        """ Returns a dictionary with all leaderboard attributes. """
        return {
            "title": self.leaderboardTitle,
            "order": self.leaderboardOrder,
            "score": self.leaderboardScore,
        }

    @property
    def leaderboardTitle(self) -> str:
        """ Returns the leaderboard title attribute for the test. """
        return getattr(self.getTest(), "_g_leaderboard_title", None)

    @leaderboardTitle.setter
    def leaderboardTitle(self, title) -> None:
        """ Sets the leaderboard title attribute. """
        self.setattr("_g_leaderboard_title", title)

    @property
    def leaderboardOrder(self) -> str:
        """ Return the leaderboard order attribute. """
        return getattr(self.getTest(), "_g_leaderboard_order", None)

    @leaderboardOrder.setter
    def leaderboardOrder(self, order) -> None:
        """ Sets the leaderboard order attribute. """
        self.setattr("_g_leaderboard_order", order)

    @property
    def leaderboardScore(self) -> Union[int, None]:
        return getattr(self.getTest(), "_g_leaderboard_score", None)

    @leaderboardScore.setter
    def leaderboardScore(self, score) -> None:
        """ Sets the leaderboard score for the test. """
        self.setattr("_g_leaderboard_score", score)
