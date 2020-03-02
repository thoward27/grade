import logging
from collections import deque
from typing import Iterator, Union, List
from itertools import cycle
from typing import Iterable

from .pipeline import Pipeline


class PartialCredit:
    """ Executes a list of pipelines, assigning credit for each successful run.

    If value is a single integer, its' value is distributed between all pipelines;
    if value is a list of integers, the values from the list are assigned sequentially
    to the pipelines and, if the length of the list is not equal to the number of
    pipelines, it wraps the values and repeats the first entries in the list.

    Example:
    A = Pipeline
    B = Pipeline
    C = Pipeline
    PartialCredit([A, B, C], [1, 2])
    A.max_score == 1
    B.max_score == 2
    C.max_score == 1

    :param pipelines: an iterator of Pipeline objects.
    :param value: total value for the pipeline; either an int, or a list of ints (accessed via modulo arithmetic).
    """

    def __init__(self, pipelines: Iterator[Pipeline], value: Union[int, List[int]]):
        self.pipelines = list(pipelines)

        if isinstance(value, Iterable):
            self.value = deque([v for (v, _) in zip(cycle(value), range(len(self.pipelines)))])
        else:
            self.value = deque([value / len(self.pipelines) for _ in range(len(self.pipelines))])

        self.max_score = sum(self.value)
        self._score = 0
        self._executed = False

    @property
    def score(self) -> float:
        """ Returns the aggregate score, raises exception if not run. """
        assert self._executed
        return min(self.max_score, round(self._score, 2))

    def __call__(self):
        self._executed = True
        for pipeline in self.pipelines:
            try:
                pipeline()
            except Exception as e:
                logging.exception(e, exc_info=False)
            else:
                self._score += self.value[0]
            finally:
                self.value.popleft()
        return self
