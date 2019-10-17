""" Mixins.
"""
from inspect import stack, getmembers, ismethod
from typing import List, Callable
from collections import namedtuple

class ScoringMixin:

    methods : List[tuple] = None

    def __str__(self) -> str:
        return type(self).__name__

    def getTest(self) -> Callable:
        """ Returns the topmost testing function on the stack. """
        if not self.methods:
            self.methods = getmembers(self, predicate=ismethod)
        
        caller = [frame for frame in stack() if frame.function.startswith('test')][0]
        caller = [func for name, func in self.methods if name == caller.function][0]
        return caller

    @property
    def weight(self) -> int:
        return getattr(self.getTest().__dict__, '__weight__', 0)

    @weight.setter
    def weight(self, weight):
        self.getTest().__dict__['__weight__'] = weight

    @property
    def score(self):
        return getattr(self.getTest().__dict__, '__score__', 0)
    
    @score.setter
    def score(self, score):
        self.getTest().__dict__['__score__'] = score

    @property
    def visibility(self):
        return getattr(self.getTest().__dict__['__visibility__'], 'visible')

    def visibility(self, visibility):
        self.getTest().__dict__['__visibility__'] = visibility

    @property
    def leaderboard(self) -> dict:
        return {
            'title': getattr(self.getTest(), '__leaderboard_title__', None),
            'order': getattr(self.getTest(), '__leaderboard_order__', None),
            'score': getattr(self.getTest(), '__leaderboard_score__', None)
        }

    def leaderboard(self, **kwargs):
        assert(all([p.startswith('__leaderboard') for p in kwargs.keys()]))
        self.getTest().__dict__.update(**kwargs)
