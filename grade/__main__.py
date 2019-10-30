
import argparse
import unittest
import logging

from grade.runners import GradedRunner

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Required
    parser.add_argument('context', help="Where to start looking for tests.")

    # Optional
    parser.add_argument('-p', '--pattern', default="test*", help="Glob pattern to find test files.")

    # Output related.
    parser.add_argument('--json', action='store_true')

    args = parser.parse_args()

    suite = unittest.defaultTestLoader.discover(args.context, args.pattern)
    results = GradedRunner(visibility='visible').run(suite)
    
    if args.json:
        print(results.json)
    else:
        logging.warning('No output directive found. Ran successfully.')
