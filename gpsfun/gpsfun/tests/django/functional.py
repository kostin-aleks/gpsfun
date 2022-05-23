#!/usr/bin/env python
"""
functional
"""

import os
import unittest


unittest.main.USAGE = """\
Usage: %(progName)s [options] [test] [...]

Options:
  -h, --help       Show this message
  -v, --verbose    Verbose output
  -q, --quiet      Minimal output

Examples:
  %(progName)s                               - run all default tests
  %(progName)s test_Module                   - run all test_Module tests
  %(progName)s test_Module.MyTestCase        - run all test case tests
  %(progName)s test_Module.MyTestCase.test_1 - run single test
  %(progName)s test_Module.my_test_suite     - run single test suite

  Note: Every test module should be named like test_xxx.py

To debug:
  export DEBUG_TEST=True

"""

# modules excluded from default testing
SKIP_DEFAULT = ['test_databrowse', 'test_Demo']

test_dir = os.path.dirname(os.path.abspath(__file__))

all_modules = [
    os.path.splitext(f)[0]
    for f in os.listdir(test_dir)
    if f.startswith('test_') and f.endswith('.py')]

default_modules = [m for m in all_modules if m not in SKIP_DEFAULT]

default_suite = unittest.defaultTestLoader.loadTestsFromNames(default_modules)

if __name__ == '__main__':
    unittest.main(defaultTest='default_suite')
