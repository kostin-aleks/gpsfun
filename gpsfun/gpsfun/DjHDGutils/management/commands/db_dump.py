from optparse import make_option
from django.conf import settings
import os
import datetime
import logging

from django.core.management.base import BaseCommand, CommandError
from DjHDGutils import shell_utils as hdgshell

from DjHDGutils.dbutils import db_config
from distutils import dir_util

def _sqldumps_path():
    path = settings.SITE_ROOT + 'dumps/' + 'sql/'
    if hasattr(settings, 'SQLDUMPS_PATH'):
        path = settings.SQLDUMPS_PATH

    if not os.path.exists(path):
        logging.warn('Creating sqldumps folder: "%s"' % path)
        dir_util.mkpath(path)

    return path


def restore_dbdump(options):
    if options['file']:
        fromfile = options['file']
    else:
        fromfile = hdgshell.cmd_read(
            'ls -1tr %s*.sql.bz2|tail -n 1' % _sqldumps_path()).strip()

    print 'Restore from: %s' % fromfile
    params = []

    if db_config.host:
        params.append('-h %s' % db_config.host)

    if db_config.engine.startswith('postgres'):

        if db_config.user:
            params.append('-U %s' % db_config.user)

        try:
            hdgshell.startprocess(
                'dropdb %s %s ; ' % (' '.join(params),
                                     db_config.name))
        except:
            pass

        hdgshell.startprocess(
            'createdb %s %s ; ' % (' '.join(params),
                                   db_config.name))

        hdgshell.startprocess(
            'bzcat %s | ./manage.py dbshell' % fromfile)

    elif db_config.engine.startswith('postgis'):

        if db_config.user:
            params.append('-U %s' % db_config.user)

        try:
            hdgshell.startprocess(
                'dropdb %s %s ; ' % (' '.join(params),
                                     db_config.name))
        except:
            pass

        hdgshell.startprocess(
            'createdb %s %s; ' % (' '.join(params),
                                                      db_config.name))

        hdgshell.startprocess(
            'bzcat {fromfile} | psql -U postgres -d {db_name}'.format(
                fromfile=fromfile, db_name=db_config.name))

    elif db_config.engine.startswith('mysql'):
        hdgshell.startprocess(
            'echo "drop database %s ; '\
            'create database %s"| ./manage.py dbshell' % (
                db_config.name,
                db_config.name))

        if db_config.user:
            params.append('-u %s' % db_config.user)

        if db_config.password:
            params.append("-p'%s'" % db_config.password)

        if db_config.port:
            params.append("-P %s" % db_config.port)

        cmd = 'bzcat {fromfile} | mysql -f {params} {dbname}'.format(
            fromfile=fromfile,
            dbname=db_config.name,
            params=' '.join(params))
        print cmd
        hdgshell.startprocess(cmd)


def make_dbdump(options):
    todir = _sqldumps_path()
    tofile = options['file']
    if not tofile:
        today = datetime.date.today()
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%T')
        tofile = '%s%s.sql.bz2' % (todir, timestamp)
    elif not '/' in tofile:
        tofile = todir + tofile
    else:
        todir = os.path.split(tofile)[0]

    execstr = db_dump_runcmd(db_config, tofile, options['dumpargs'])
    os.system(execstr)

    if os.path.exists(tofile):
        print tofile
    else:
        raise CommandError('Command failed: %s' \
                           % execstr)


def db_dump_runcmd(dbconfig, tofile, dumpargs):
    if db_config.engine.startswith('postgresql') or db_config.engine.startswith('postgis'):
        params = []
        if db_config.host:
            params.append(('-h', db_config.host))

        if db_config.user:
            params.append(('-U', db_config.user))

        if db_config.name:
            params.append(('', db_config.name))

        if db_config.password:
            os.environ['PGPASSWORD'] = db_config.password

        if db_config.engine.startswith('postgres'):
            execargs = '-O'
        else:
            execargs = ''

        dumpargs = (dumpargs or '') + execargs

        execstr = 'pg_dump %(execargs)s %(dbparams)s | bzip2 '\
                  '> %(tofile)s' % \
                  (dict(dbparams=' '.join(["%s %s" % (p[0], p[1]) \
                                           for p in params]),
                        execargs=dumpargs,
                        tofile=tofile))
    elif db_config.engine.startswith('mysql'):
        s = ''
        if db_config.host:
            s += " -h %s" % db_config.host

        if db_config.user:
            s += " -u'%s'" % db_config.user

        if db_config.password:
            s += " -p'%s'" % db_config.password

        if db_config.name:
            s += ' ' + db_config.name

        # skip-opt added so tables are not locked during dump
        s += ' --skip-opt  --add-drop-table --add-locks'\
             ' --create-options --disable-keys'\
             ' --extended-insert  --quick --set-charset'


        execstr = 'mysqldump %(args)s | bzip2 '\
                  '> %(tofile)s' % \
                  (dict(args=s,
                        tofile=tofile))
    elif db_config.engine.startswith('sqlite3'):
        execstr = 'cat %s | bzip2 > %s' % (db_config.name,
                                           tofile)
    else:
        raise CommandError('Database engine %s is not supported yet.' \
                           % dbconfig.engine)
    return execstr


class Command(BaseCommand):
    help = ("Make current database dump.")

    option_list = BaseCommand.option_list + (
        make_option('--file', action='store', dest='file',
                    help='File to store dump.'),
        make_option('--dump-args', action='store', dest='dumpargs',
                    help='Dump program arguments.'),
        make_option('--restore', action='store_true', dest='restore',
                    help='restore dump.'),
    )

    requires_model_validation = False

    def handle(self, **options):
        if options['restore']:
            restore_dbdump(options)
        else:
            make_dbdump(options)
