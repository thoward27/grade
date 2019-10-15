""" Mixins.
"""
import inspect
from inspect import stack, getmembers, ismethod

class TestMixin:

    methods = None
    _ignore = ['score', 'getTest']

    def __str__(self):
        return type(self).__name__

    def getTest(self):
        """ Returns the topmost test function on the stack. """
        if not self.methods:
            self.methods = getmembers(self, predicate=ismethod)
        caller = [frame for frame in stack() if frame.function.startswith('test')][0]
        caller = [func for name, func in self.methods if name == caller.function][0]
        return caller

    @property
    def score(self):
        return getattr(self.getTest().__dict__, '__score__', 0)
 
    def score(self, score):
        self.getTest().__dict__['__score__'] = score
        return
