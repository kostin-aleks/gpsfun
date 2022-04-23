"""
db dump
"""
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
    """ path to sql dump """
    path = settings.SITE_ROOT + 'dumps/' + 'sql/'
    if hasattr(settings, 'SQLDUMPS_PATH'):
        path = settings.SQLDUMPS_PATH

    if not os.path.exists(path):
        logging.warn(f'Creating sqldumps folder: "{path}"')
        dir_util.mkpath(path)

    return path


def restore_dbdump(options):
    """ restore db dump """
    if options['file']:
        fromfile = options['file']
    else:
        path = _sqldumps_path()
        fromfile = hdgshell.cmd_read(
            'ls -1tr {path}*.sql.bz2|tail -n 1').strip()

    print(f'Restore from: {fromfile}')
    params = []

    if db_config.host:
        params.append(f'-h {db_config.host}')

    if db_config.engine.startswith('postgres'):

        if db_config.user:
            params.append(f'-U {db_config.user}')

        try:
            param_string = ' '.join(params)
            hdgshell.startprocess(
                f'dropdb {param_string} {db_config.name} ; ')
        except:
            pass

        param_string = ' '.join(params)
        hdgshell.startprocess(
            f'createdb {param_string} {db_config.name} ; ')

        hdgshell.startprocess(
            f'bzcat {fromfile} | ./manage.py dbshell')

    elif db_config.engine.startswith('postgis'):

        if db_config.user:
            params.append(f'-U {db_config.user}')

        try:
            param_string = ' '.join(params)
            hdgshell.startprocess(
                f'dropdb {param_string} {db_config.name} ; ')
        except:
            pass

        param_string = ' '.join(params)
        hdgshell.startprocess(
            f'createdb {param_string} {db_config.name}; ')

        hdgshell.startprocess(
            f'bzcat {fromfile} | psql -U postgres -d {db_config.name}')

    elif db_config.engine.startswith('mysql'):
        hdgshell.startprocess(
            f'echo "drop database {db_config.name} ; '
            'create database {db_config.name}"| ./manage.py dbshell')

        if db_config.user:
            params.append(f'-u {db_config.user}')

        if db_config.password:
            params.append(f"-p'{db_config.password}'")

        if db_config.port:
            params.append(f"-P {db_config.port}")

        params = ' '.join(params)
        cmd = f'bzcat {fromfile} | mysql -f {params} {db_config.name}'
        print(cmd)
        hdgshell.startprocess(cmd)


def make_dbdump(options):
    """ make db dump """
    todir = _sqldumps_path()
    tofile = options['file']
    if not tofile:
        today = datetime.date.today()
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%T')
        tofile = f'{todir}{timestamp}.sql.bz2'
    elif not '/' in tofile:
        tofile = todir + tofile
    else:
        todir = os.path.split(tofile)[0]

    execstr = db_dump_runcmd(db_config, tofile, options['dumpargs'])
    os.system(execstr)

    if os.path.exists(tofile):
        print(tofile)
    else:
        raise CommandError(f'Command failed: {execstr}')


def db_dump_runcmd(dbconfig, tofile, dumpargs):
    """ run command """
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

        dbparams = ' '.join(["%s %s" % (p[0], p[1]) for p in params])
        execstr = f'pg_dump {dumpargs} {dbparams} | bzip2 > {tofile}'

    elif db_config.engine.startswith('mysql'):
        s = ''
        if db_config.host:
            s += f" -h {db_config.host}"

        if db_config.user:
            s += f" -u'{db_config.user}'"

        if db_config.password:
            s += f" -p'{db_config.password}'"

        if db_config.name:
            s += ' ' + db_config.name

        # skip-opt added so tables are not locked during dump
        s += ' --skip-opt  --add-drop-table --add-locks'\
             ' --create-options --disable-keys'\
             ' --extended-insert  --quick --set-charset'

        execstr = f'mysqldump {s} | bzip2 > {tofile}'

    elif db_config.engine.startswith('sqlite3'):
        execstr = f'cat {db_config.name} | bzip2 > {tofile}'
    else:
        raise CommandError(f'Database engine {dbconfig.engine} is not supported yet.')
    return execstr


class Command(BaseCommand):
    """ Command """
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
