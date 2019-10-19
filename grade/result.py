from typing import TextIO
from unittest import result
import unittest
import json
import io


class Result(unittest.TextTestResult):
    """ A unit test TestCase result.
    """

    def __init__(self,
                 stream: TextIO,
                 descriptions: bool,
                 verbosity: int) -> None:
        super().__init__(stream, descriptions, verbosity)
        self.data = {
            'tests': [],
            'leaderboard': [],
        }

    @property
    def json(self) -> dict:
        return self.data

    @property
    def markdown(self) -> str:
        raise NotImplementedError

    @staticmethod
    def getattr(test, attribute, default=None):
        return getattr(getattr(test, test._testMethodName), attribute, default)

    @staticmethod
    def parseExceptions(failures, errors):
        output = ''.join([*failures, *errors])
        output = '; '.join([line.strip() for line in output.split('\n')[1:]])
        # Shave output to: final python file, failures/errors
        output = ''.join([output.split('.py')[-2].split('/')[-1] + '.py', output.split('.py\"')[-1]])
        return output.strip()

    def stopTest(self, test):
        super().stopTest(test)
        # Basic Information
        result = {
            'name': self.getattr(test, '__name__'),
            'max_score': self.getattr(test, '__weight__', 0),
            'score': self.getattr(test, '__score__', None),
        }

        # Add to name.
        if description := test.shortDescription():
            result['name'] = result['name'] + ': ' + description

        # Parse any exceptions out.
        failures = [msg for func, msg in self.failures if func == test]
        errors = [msg for func, msg in self.errors if func == test]
        if failures or errors:
            result['output'] = self.parseExceptions(failures, errors)

        # Update score if needed.
        if result['score'] is None:
            result['score'] = 0 if failures or errors else result['max_score']
        
        # Append the result.
        self.data['tests'].append(result)
        
        # Update leaderboard, if needed.
        if self.getattr(test, '__leaderboard_title__') is not None:
            self.data['leaderboard'].append({
                'name': self.getattr(test, '__leaderboard_title__'),
                'value': self.getattr(test, '__leaderboard_score__'),
                'order': self.getattr(test, '__leaderboard_order__'),
            })
        return
