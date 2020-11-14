#!/var/www/kostin1/www.GPS-FUN.INFO/env/bin/python
# -*- coding: utf-8 -*-
import sys, os
os.environ.setdefault('PATH', '/bin:/usr/bin')
os.environ['PATH'] = '/var/www/kostin1/www.GPS-FUN.INFO/env/bin:' + os.environ['PATH']
os.environ['VIRTUAL_ENV'] = '/var/www/kostin1/www.GPS-FUN.INFO/env/bin'
os.environ['PYTHON_EGG_CACHE'] = '/var/www/kostin1/www.GPS-FUN.INFO/env/egg_cache'
# file creation mode
os.umask(022)

# Add a custom Python path.
sys.path.insert(0, "/var/www/kostin1/www.GPS-FUN.INFO/")

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "gpsfun.settings"

from django.core.servers.fastcgi import runfastcgi
runfastcgi(["method=threaded", "daemonize=false"])
