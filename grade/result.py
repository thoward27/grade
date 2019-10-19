from typing import TextIO
from unittest import result
import unittest
import json
import io


class Result(unittest.TextTestResult):

    def __init__(self,
                 stream: TextIO,
                 descriptions: bool,
                 verbosity: int) -> None:
        super().__init__(stream, descriptions, verbosity)
        self.data = {
            'tests': [],
            'leaderboard': [],
            'visibility': 'visible',
            'execution_time': 0.0,
        }

    @property
    def json(self):
        return self.data

    @property
    def markdown(self):
        raise NotImplementedError

    @staticmethod
    def get(test, attribute, default=None):
        return getattr(getattr(test, test._testMethodName), attribute, default)

    def stopTest(self, test):
        super().stopTest(test)
        results = {
            'name': self.get(test, '__name__'),
            'max_score': self.get(test, '__weight__', 0),
            'score': self.get(test, '__score__', None)
        }

        if description := test.shortDescription():
            results['name'] = results['name'] + ': ' + description

        failures = [msg for func, msg in self.failures if func == test]
        errors = [msg for func, msg in self.errors if func == test]
        if failures or errors:
            results['output'] = ''.join([*failures, *errors])

        if results['score'] is None:
            results['score'] = 0 if failures or errors else results['max_score']
        
        self.data['tests'].append(results)

        if self.get(test, '__leaderboard_title__') is not None:
            self.data['leaderboard'].append({
                'name': self.get(test, '__leaderboard_title__'),
                'value': self.get(test, '__leaderboard_score__'),
                'order': self.get(test, '__leaderboard_order__'),
            })
        return
