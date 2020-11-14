#!/home/kostin/dev/www.GPS-FUN.INFO/env/bin/python
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


"""
import os
import sys

os.environ.setdefault('PATH', '/bin:/usr/bin')
os.environ['PATH'] = '/var/www/htdocs/env/bin:' + os.environ['PATH']
os.environ['VIRTUAL_ENV'] = '/var/www/htdocs/env/bin'
os.environ['PYTHON_EGG_CACHE'] = '/var/www/htdocs/env/egg_cache'
# file creation mode
os.umask(022)

# Add a custom Python path.
sys.path.insert(0, "/var/www/htdocs/")

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "gpsfun.settings"
core_bin_dir = os.path.dirname(os.path.abspath((sys.argv[0])))
SITE_ROOT = os.path.normpath(os.path.join(core_bin_dir, '../..'))

os.putenv('PYTHONPATH', SITE_ROOT)

if len(sys.argv) > 1:
    try:
        os.execv(sys.argv[1], sys.argv[1:])   # arg0=$1, arg1=$2...
    except Exception, e:
        print "Error running '%s' process: '%s'" % (sys.argv[1:], e)
        raise
else:
    print __doc__
