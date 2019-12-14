""" Decorators.

Inspired by Gradescope-utils.
https://github.com/gradescope/gradescope-utils
"""

from functools import wraps, partial


def static(name, value):
    """ Sets name to value.
    """

    def decorate(func):
        """ Set name to value. """
        setattr(func, name, value)
        return func

    return decorate


weight = partial(static, '__weight__')
weight.__doc__ = \
    """ Simple decorator to add a __weight__ property to a function
    
    Usage: @weight(3.0)
    """

visibility = partial(static, '__visibility__')
visibility.__doc__ = \
    """ Simple decorator to add a __visibility__ property to a function
    
    Usage: @visibility("hidden")
    
    Options for the visibility field are as follows:
    - `hidden`: test case will never be shown to students
    - `after_due_date`: test case will be shown after the assignment's due date has passed
    - `after_published`: test case will be shown only when the assignment is explicitly published
    - `visible` (default): test case will always be shown
    """


def leaderboard(name=None, order='desc'):
    """ Decorator that indicates that a test corresponds to a leaderboard column

    Usage: @leaderboard(column title, ordering)
    By default, column title and ordering are 
    function.__name__ and 'desc' respectively.

    You may pass in any column title you'd like, however
    ordering must be either 'asc' or 'desc'

    Then, within the test, set the value by calling
    kwargs['set_leaderboard_value'] with a value. You can make this convenient by
    explicitly declaring a set_leaderboard_value keyword argument, eg.

    .. code-block:: python3

        def test_highscore(set_leaderboard_score=None):
            set_leaderboard_score(42)

    You can also use the ScoringMixin, 
    which provides a setter for leaderboardScore.
    """

    def decorate(func):
        setattr(func, '__leaderboard_title__', name if name else func.__name__)
        setattr(func, '__leaderboard_order__', order)
        setattr(func, '__leaderboard_score__', None)

        def set_score(value):
            setattr(wrapper, '__leaderboard_score__', value)

        @wraps(func)
        def wrapper(*args, **kwargs):
            kwargs['set_leaderboard_score'] = set_score
            return func(*args, **kwargs)

        return wrapper

    return decorate
