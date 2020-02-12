import io
import time
from typing import Optional, TextIO, Type
from unittest import TextTestRunner

from grade.result import Result


class GradedRunner(TextTestRunner):
    def __init__(self,
                 stream: Optional[TextIO] = io.StringIO(),
                 descriptions: bool = True,
                 verbosity: int = 0,
                 failfast: bool = False,
                 buffer: bool = True,
                 warnings: Optional[Type[Warning]] = None,
                 *,
                 tb_locals: bool = False,
                 visibility: 'str' = 'visible') -> None:
        super().__init__(stream, descriptions, verbosity, failfast, buffer, Result, warnings, tb_locals=tb_locals)
        self.visibility = visibility

    def run(self, test) -> Result:
        start = time.time()
        # noinspection PyTypeChecker
        results: Result = super().run(test)
        results.data['execution_time'] = round(time.time() - start)
        results.data['visibility'] = self.visibility

        if len(results.data['tests']) == 0:
            # setUpClass failed.
            tests = [m for t in test for m in t.getTests()]
            results.data['tests'] = [
                {
                    'name': t.__qualname__, 
                    'max_score': 0, 
                    'score': '0', 
                    'output': ';\n'.join([f'{e[0]}: {e[1]}' for e in results.errors]),
                }
                for k, t in tests]

        return results
