from unittest import result


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
