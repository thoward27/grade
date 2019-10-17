""" Modified Decorators Derived from Gradescope-utils.

https://github.com/gradescope/gradescope-utils/blob/master/gradescope_utils/autograder_utils/decorators.py
"""

from gradescope_utils.autograder_utils.decorators import weight, visibility

class weight(object):
    """Simple decorator to add a __weight__ property to a function
    Usage: @weight(3.0)
    """
    def __init__(self, val):
        self.val = val

    def __call__(self, func):
        func.__weight__ = self.val
        return func


class visibility(object):
    """Simple decorator to add a __visibility__ property to a function
    Usage: @visibility("hidden")
    Options for the visibility field are as follows:
    - `hidden`: test case will never be shown to students
    - `after_due_date`: test case will be shown after the assignment's due date has passed
    - `after_published`: test case will be shown only when the assignment is explicitly published from the "Review Grades" page
    - `visible` (default): test case will always be shown
    """

    def __init__(self, val):
        self.val = val

    def __call__(self, func):
        func.__visibility__ = self.val
        return func


class leaderboard(object):
    """Decorator that indicates that a test corresponds to a leaderboard column
    Usage: @leaderboard("high_score"). The string parameter indicates
    the name of the column on the leaderboard
    Then, within the test, set the value by calling
    kwargs['set_leaderboard_value'] with a value. You can make this convenient by
    explicitly declaring a set_leaderboard_value keyword argument, eg.
    ```
    def test_highscore(set_leaderboard_value=None):
        set_leaderboard_value(42)
    ```
    """

    def __init__(self, column_name, sort_order='desc'):
        self.column_name = column_name
        self.sort_order = sort_order

    def __call__(self, func):
        func.__leaderboard_column__ = self.column_name
        func.__leaderboard_sort_order__ = self.sort_order

        def set_leaderboard_value(x):
            wrapper.__leaderboard_value__ = x

        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs['set_leaderboard_value'] = set_leaderboard_value
            return func(*args, **kwargs)

        return wrapper
