#!/usr/bin/env python
import os
import sys
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
#path = '%s/../../' % test_dir
#if path not in sys.path:
   #sys.path.append(path)
#print path
# virtualenv
#SITE_ROOT = os.path.normpath(os.path.join(test_dir, '../../../'))
#virtualenv_dir = SITE_ROOT + '/env'
#print virtualenv_dir
#if os.path.exists(virtualenv_dir):
    #ACTIVATE_THIS = SITE_ROOT+'/env/bin/activate_this.py'
    #print ACTIVATE_THIS
    #execfile(ACTIVATE_THIS, dict(__file__=ACTIVATE_THIS))


all_modules = [os.path.splitext(f)[0]
               for f in os.listdir(test_dir)
               if f.startswith('test_') and f.endswith('.py')]

default_modules = [m for m in all_modules if m not in SKIP_DEFAULT]

# import test_xxx
#for m in all_modules:
    #print m
    #globals()[m] = __import__(m)

default_suite = unittest.defaultTestLoader.loadTestsFromNames(default_modules)

if __name__ == '__main__':
    unittest.main(defaultTest='default_suite')
