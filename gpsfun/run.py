#!/usr/bin/env python
"""
NAME
     run.py

DESCRIPTION
     Execute command with django environment configured for current djw
     project

SYNOPSIS
     run.py command [argument ...]

PARAMETERS
     command - any executable (binary or script like shell, python, etc)
     argument - any amount of arguments passed to command.

EXAMPLES

"""
import os
import sys


SITE_ROOT = os.path.realpath(os.path.join(
    os.path.dirname(__file__), '')) + '/gpsfun/'
print(SITE_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gpsfun.settings")
os.environ.setdefault('PYTHONPATH', SITE_ROOT)

import django

django.setup()

if len(sys.argv) > 1:
    try:
        os.execv(sys.argv[1], sys.argv[1:])   # arg0=$1, arg1=$2...
    except Exception as e:
        print("Error running '%s' process: '%s'" % (sys.argv[1:], e))
        raise
else:
    print(__doc__)

