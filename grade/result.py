from typing import TextIO
from unittest import result
import unittest
import json
import io


class JSONResult(unittest.TextTestResult):

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

    def save(self, filename: str = None):
        if not filename:
            self.stream.truncate(0)
            self.stream.seek(0)
        json.dump(self.data, filename if filename else self.stream)
        return self

    @staticmethod
    def get(test, attribute, default=None):
        return getattr(getattr(test, test._testMethodName), attribute, default)

    def stopTest(self, test):
        super().stopTest(test)
        results = {
            'name': self.get(test, '__name__'),
            'max_score': self.get(test, '__weight__', 0)
        }
        results['score'] = self.get(test, '__score__', results['max_score'])

        if description := test.shortDescription():
            results['name'] = results['name'] + ': ' + description

        failures = [msg for func, msg in self.failures if func == test]
        errors = [msg for func, msg in self.errors if func == test]
        if failures or errors:
            results['output'] = ''.join([*failures, *errors])
        
        self.data['tests'].append(results)

        if self.get(test, '__leaderboard_title__') is not None:
            self.data['leaderboard'].append({
                'name': self.get(test, '__leaderboard_title__'),
                'value': self.get(test, '__leaderboard_score__'),
                'order': self.get(test, '__leaderboard_order__'),
            })


class TestResult(result.TestResult):

    def description(self, test):
        if line := test.shortDescription() is not None:
            return line
        else:
            return str(test)

    def weight(self, test):
        return getattr(getattr(test, test._testMethodName), '__weight__', 0.0)

    def score(self, test):
        return getattr(getattr(test, test._testMethodName), '__score__', None)

    def visibility(self, test):
        return getattr(getattr(test, test._testMethodName), '__visibility__', None)

    def leaderboard(self, test):
        return {
            'title': getattr(getattr(test, test._testMethodName), '__leaderboard_title__', None),
            'order': getattr(getattr(test, test._testMethodName), '__leaderboard_order__', None),
            'value': getattr(getattr(test, test._testMethodName), '__leaderboard_score__', None)
        }
