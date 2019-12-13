""" Pipeline: Autograding Executable Files

Pipeline components allow you chain together tests
for executable files within a few lines, without the
headaches of typical executable testing.
"""
from typing import Callable

from .completedprocess import CompletedProcess

Callback = Callable[[CompletedProcess], CompletedProcess]


class Pipeline:
    """ Takes callbacks and executes them sequentially when called.

    Used for grading executable files or scripts, as it allows
    you to chain together Run() with things like AssertExitSuccess().

    It does this by passing a CompletedProcess object to each successive
    callback, allowing each callback to modify or replace it during 
    execution of the pipeline. 

    All Pipelines should start with a call to Run().

    Raises an exception if any assertions or run commands fail.
    """

    def __init__(self, *callbacks: Callback):
        self.callbacks = callbacks

    def __call__(self) -> CompletedProcess:
        results = None
        for callback in self.callbacks:
            temp = callback(results)
            results = temp if type(temp) is CompletedProcess else results
        return results

    def __iter__(self) -> Callback:
        for callback in self.callbacks:
            yield callback

    def __getitem__(self, index) -> Callback:
        return self.callbacks[index]

    def __len__(self) -> int:
        return len(self.callbacks)


class Lambda:
    """ Execute arbitrary code in a Pipeline. """

    def __init__(self, function: Callable[[any], any]):
        self.function = function

    def __call__(self, results: CompletedProcess) -> CompletedProcess:
        results = self.function(results)
        return results
