# Grade: Get Readymade Autograding Done Efficiently

A utility for programming assignment autograding.

## Motivation

Grade attempts alleviate typical problems in autograding workflows.
By providing easy-to-use wrappers to work directly with executable files, Grade can test almost anything.
Combining that with the `ScoringMixin` and the `GradedRunner`, allows you to output your scores for Gradescope or an in-house Markdown report.

[![Documentation Status](https://readthedocs.org/projects/grade/badge/?version=latest)](https://grade.readthedocs.io/en/latest/?badge=latest)

---

## Documentation

https://grade.readthedocs.io/en/latest/

## Setup

### Pip

`python -m pip install grade`

### Docker

```docker
FROM thoward27/grade:latest
```

## Quickstart

1. Create a `unittest.TestCase`
2. Optionally, add in the `grade.mixins.ScoringMixin`
3. For each question, you can use `@grade.decorators.weight(x)` or `self.weight = x` to set the weight of a question.
4. If you wish to assign partial credit for some portion of a test, you can use `self.score = x`. (Warning: if you leave a test with partial credit, the student will receive that score, to give full credit at the end simply run `self.score = self.weight`)
5. Run the tests using `grade.runners.GradedRunner().run(TestSuite)`, which returns a `Result` object.
6. Once you have the results, you can output them to `json` via the property `results.json`

### Gradescope

To properly output scores for Gradescope, simply write the `json` results to `/autograder/results/results.json`

#### Option 1: Redirection

Given the following python snippet at the end of your test file:

```python
import unittest
from grade.runners import GradedRunner
if __name__ == "__main__":
    suite = unittest.TestLoader().discover('./', pattern='test*')
    print(GradedRunner().run(suite).json)
```

Simply redirect the output:

```bash
python test.py > autograder/results/results.json
```

#### Option 2: Direct Writing

Of course, you can also write directly to the file in your code.

> Ensure you only do this in one place, or it may overwrite your work!

```python
import unittest
from grade.runners import GradedRunner

if __name__ == "__main__":
    suite = unittest.TestLoader().discover('./', pattern='test*')
    results = GradedRunner().run(suite)
    with open('/autograder/results/results.json', 'w') as f:
        f.write(results.json)
```
