""" Mixins.
"""
from inspect import stack, getmembers, ismethod
from typing import List, Callable
from collections import namedtuple

class ScoringMixin:
    """ Provides scoring utility functions.
    """

    methods : List[tuple] = None

    def __str__(self) -> str:
        return type(self).__name__

    def getTests(self) -> List[Callable]:
        """ Returns a list of all test methods. """
        return [(key, getattr(self, key)) for key in dir(self) if key.startswith('test')]


    def getTest(self) -> Callable:
        """ Returns the topmost test method on the stack. """
        if not self.methods:
            self.methods = self.getTests()
        
        caller = [frame for frame in stack() if frame.function.startswith('test')][0]
        caller = [func for name, func in self.methods if name == caller.function][0]
        return caller

    @property
    def weight(self) -> int:
        """ Returns the weight of the test. """
        return getattr(self.getTest().__dict__, '__weight__', 0)

    @weight.setter
    def weight(self, weight: int) -> None:
        """ Sets the weight of the test. """
        self.getTest().__dict__['__weight__'] = weight

    @property
    def score(self) -> Union[int, float]:
        """ Returns the current score for the test. """
        return getattr(self.getTest().__dict__, '__score__', 0)
    
    @score.setter
    def score(self, score: Union[int, float]) -> None:
        """ Sets the score for the test. """
        self.getTest().__dict__['__score__'] = score

    @property
    def visibility(self) -> str:
        """ Returns visibility of the test. 
        
        This controls whether or not students should see the failing testcase.
        """
        return getattr(self.getTest().__dict__['__visibility__'], 'visible')

    @visibility.setter
    def visibility(self, visibility: str) -> None:
        """ Sets the visibility of the test. """
        self.getTest().__dict__['__visibility__'] = visibility

    @property
    def leaderboard(self) -> dict:
        """ Returns a dictionary with all leaderboard attributes. """
        return {
            'title': getattr(self.getTest(), '__leaderboard_title__', None),
            'order': getattr(self.getTest(), '__leaderboard_order__', None),
            'score': getattr(self.getTest(), '__leaderboard_score__', None)
        }

    def leaderboard(self, **kwargs) -> None:
        """ Updates leaderboard attributes.
        
        All attributes must start with __leaderboard.
        """
        assert(all([p.startswith('__leaderboard') for p in kwargs.keys()]))
        self.getTest().__dict__.update(**kwargs)
