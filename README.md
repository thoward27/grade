# Grade: Get Readymade Autograding Done Efficiently

A utility for programming assignment grading.

## Motivation

Autograding is a challenge when the language doesn't support proper unit testing, or when you need to test binary files, grade solves these problems.

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
if __name__ == "__main__":
    suite = unittest.TestLoader().discover('./', pattern='test*')
    print(runners.GradedRunner().run(suite).json)
```

Simply redirect the output:

```bash
python test.py > autograder/results/results.json
```

#### Option 2: Direct Writing

Of course, you can also write directly to the file in your code.

> Ensure you only do this in one place, or it may overwrite your work!

```python
if __name__ == "__main__":
    suite = unittest.TestLoader().discover('./', pattern='test*')
    results = runners.GradedRunner().run(suite).json
    with open('/autograder/results/results.json', 'w') as f:
        f.write(results.json)
```
