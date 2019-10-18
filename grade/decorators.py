""" Modified Decorators Derived from Gradescope-utils.

https://github.com/gradescope/gradescope-utils/blob/master/gradescope_utils/autograder_utils/decorators.py
"""

from functools import wraps


class weight:
    """ Simple decorator to add a __weight__ property to a function
    
    Usage: @weight(3.0)
    """

    def __init__(self, val):
        self.val = val

    def __call__(self, func):
        func.__weight__ = self.val
        return func


class visibility:
    """ Simple decorator to add a __visibility__ property to a function
    
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


class leaderboard:
    """ Decorator that indicates that a test corresponds to a leaderboard column
    
    Usage: @leaderboard(column title, ordering)
    By default, column title and ordering are 
    function.__name__ and 'desc' respectively.

    You may pass in any column title you'd like, however
    ordering must be either 'asc' or 'desc'
    
    Then, within the test, set the value by calling
    kwargs['set_leaderboard_value'] with a value. You can make this convenient by
    explicitly declaring a set_leaderboard_value keyword argument, eg.

    ```
    def test_highscore(set_leaderboard_score=None):
        set_leaderboard_score(42)
    ```

    You can also use the ScoringMixin, 
    which provides a setter for leaderboardScore.
    """

    def __init__(self, name=None, order='desc'):
        self.name = name
        self.order = order

    def __call__(self, func):
        func.__leaderboard_title__ = self.name if self.name else func.__name__
        func.__leaderboard_order__ = self.order
        func.__leaderboard_score__ = None

        def set_leaderboard_score(x):
            wrapper.__leaderboard_score__ = x

        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs['set_leaderboard_score'] = set_leaderboard_score
            return func(*args, **kwargs)

        return wrapper
