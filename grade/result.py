from typing import TextIO, List, Tuple
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
        return json.dumps(self.data, indent=4, sort_keys=True) 

    @property
    def markdown(self) -> str:
        raise NotImplementedError

    @staticmethod
    def getattr(test, attribute, default=None):
        return getattr(getattr(test, test._testMethodName), attribute, default)

    @staticmethod
    def parseExceptions(exceptions):
        output = '; '.join(exceptions)
        output = '; '.join([line.strip() for line in output.split('\n')[1:] if line])
        # Shave output to: final python file, failures/errors
        output = ''.join([output.split('.py')[-2].split('/')[-1] + '.py', output.split('.py\"')[-1]])
        return output.strip()

    def getExceptions(self, test) -> List[Tuple]:
        return [m for f, m in [*self.failures, *self.errors] if f == test]

    def getName(self, test):
        name = self.getattr(test, '__name__')
        if description := test.shortDescription():
            name = f'{name}: {description}'
        return name

    def getScore(self, test):
        return self.getattr(test, '__score__', 0 if self.getExceptions(test) else self.getattr(test, '__weight__', 0))

    def addError(self, test, err):
        super().addError(test, err)
        self._mirrorOutput = False

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._mirrorOutput = False

    def stopTest(self, test):
        self.updateTests(test)
        self.updateLeaderboard(test)
        super().stopTest(test)
        return
    
    def updateTests(self, test):
        result = {
            'name': self.getName(test),
            'max_score': self.getattr(test, '__weight__', 0),
            'score': self.getScore(test),
        }
        if exceptions := self.getExceptions(test):
            result['output'] = self.parseExceptions(exceptions)
        
        elif outputs := (self._stdout_buffer.getvalue() + self._stderr_buffer.getvalue()).strip():
            result['output'] = outputs
        
        self.data['tests'].append(result)
        return


    def updateLeaderboard(self, test):
        if self.getattr(test, '__leaderboard_title__') is not None:
            self.data['leaderboard'].append({
                'name': self.getattr(test, '__leaderboard_title__'),
                'value': self.getattr(test, '__leaderboard_score__'),
                'order': self.getattr(test, '__leaderboard_order__'),
            })
        return
