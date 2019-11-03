=================================
Grade
=================================

A package designed to help alleviate autograding pain-points,
especially when grading executable files.

.. toctree::
    :hidden:
    :maxdepth: 4

    source/quickstart
    source/main
    source/pipeline
    source/decorators
    source/ScoringMixin
    source/GradedRunner

Quick Start
===============

Grade turns any `unittest.TestCase` into an autograder package.
It provides utilities to assign each testcase a maximum score,
to give partial credit, to establish leaderboards, and require files
before allotting any points. Along with all of these utilities,
Grade provides a `Pipeline` class, which takes any number of callbacks,
and then runs these callbacks in sequence. The `Pipeline` class is intended
to work with executable files, alleviating the pains of working with
`subprocess.run`, allowing you to focus on what matters, whether or not
the code runs correctly.
