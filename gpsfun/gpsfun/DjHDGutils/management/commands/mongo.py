"""
mongo
"""
import datetime
import os
from optparse import make_option
import logging

from DjHDGutils import shell_utils as hdgshell
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import shutil


def _mongo_dumps_dir():
    """ mongo dumps dir """
    todir = settings.SITE_ROOT + 'dumps/mongo/'
    for path in [os.path.split(os.path.split(todir)[0])[0],
                 os.path.split(todir)[0], todir]:
        if not os.path.exists(path):
            os.mkdir(path)
    return todir


def dump(to_file):
    """ dump """
    if not to_file:
        to_file = _mongo_dumps_dir() + \
            f"mongodb_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}.tar.bz2"

    if not to_file.endswith('.tar.bz2'):
        raise CommandError(
            'Only able to create .tar.bz2 archives: filename should end with .tar.bz2 extension.')

    to_folder = os.path.splitext(to_file)[0]
    hdgshell.startprocess(
        f'mongodump -h {settings.MONGO_HOST}:{settings.MONGO_PORT} -d {settings.MONGO_NAME} -o {to_folder}')

    os.chdir(to_folder + '/..')
    hdgshell.startprocess(
        f'tar cjf {to_file} {os.path.split(to_folder)[1]}')

    shutil.rmtree(to_folder)
    print(to_file)


def restore(fromfile):
    """ restore """
    if not fromfile:
        fromfile = hdgshell.cmd_read(
            f'ls -1tr {_mongo_dumps_dir()}*.tar.bz2|tail -n 1').strip()
    dirname = os.path.split(fromfile)[0]
    os.chdir(dirname)
    if hasattr(settings, 'MONGO_HOSTS'):
        restore_host = settings.MONGO_HOSTS[0]
    else:
        restore_host = settings.MONGO_HOST
    mongodump_dir = fromfile.replace('.tar.bz2', '')
    cmd = f'tar xf {fromfile} && cd {mongodump_dir} && '\
        'mongorestore -h {restore_host} '\
        '--drop quiz'
    # print cmd
    hdgshell.startprocess(cmd)
    shutil.rmtree(mongodump_dir)


class Command(BaseCommand):
    """ Command """
    help = ("Make Mongo database dump.")

    option_list = BaseCommand.option_list + (
        make_option('--dump', action='store_true', dest='do_dump',
                    help='Make db dump file.'),
        make_option('--restore', action='store_true', dest='do_restore',
                    help='Restore database from file.'),
        make_option('--file', action='store', dest='file',
                    help='Restore database from file.'),
    )

    requires_model_validation = False

    def handle(self, **options):
        if options['do_dump']:
            dump(options['file'])
        elif options['do_restore']:
            restore(options['file'])
        else:
            raise CommandError(
                'either --dump or --restore should be specified')
