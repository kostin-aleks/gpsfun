"""
Database patch apply managment system

"""
from optparse import make_option
import os
from datetime import datetime
import sys
import re
import imp
import stat
import random
import getpass
from subprocess import Popen
from copy import deepcopy

from django.conf import settings
from django.core.management.base import LabelCommand, CommandError
from django.db import transaction
from django import db

from DjHDGutils.dbutils import exec_sql, exec_sql_modify, db_config
from DjHDGutils.misc import atoi

VALID_FILENAME_EXTENSIONS = ['.py', '.sql', '.sh', '.php']
IGNORE_EXTENSIONS = ['.pyc']
PATCH_RE_OLD = [re.compile("^DB_patch-([\d]+)"), # DB_patch-00001.sql
                re.compile("^(\d{10})\.")]       # 1134608202.sql

# 11362-avk-512.sql
PATCH_RE_NEW = re.compile("^(\d{5})-(\w+)-(\d{3})")


@transaction.commit_manually
def check_depricated():
    try:
        exec_sql("""select count(*) from patch_log""")
        transaction.commit()
        raise CommandError("dbup command is depricated. Pls use 'patch' command now")
    except db.utils.DatabaseError:
        transaction.rollback()

def get_patch_number_by_filename(filename):
    patch_no = None
    for regexp in PATCH_RE_OLD:
        m = regexp.search(filename)
        if not m:
            continue
        patch_no = m.group(1)
    if not patch_no:
        m = PATCH_RE_NEW.search(filename)
        if m:
            lead_num, username, randpart = m.groups()
            patch_no = "%05d" % int(lead_num)+\
                       username_to_number(username)+\
                       randpart
            return patch_no
    return patch_no


def short_number(num):
    if len(str(num))>5:
        return int(str(num)[:5])
    else:
        return int(num)


def get_filename_by_number(number):
    random.seed(datetime.now())
    return "%05d-%s-%03d.sql" % (short_number(number),
                                 getpass.getuser(),
                                 random.randrange(1,999))

def username_to_number(username):
    random.seed(username)
    return "%02d" % random.randrange(0, 99)



def _patch_root_dir():
    d = getattr(settings, 'DB_PATCH_ROOT',
                settings.SITE_ROOT + 'migrations/')
    if not os.path.exists(d):
        os.mkdir(d)
    return d


class Executor(object):
    def popen(self, *args, **kwarg):
        proc = Popen(args,
                     stdin=kwarg.get('stdin', sys.stdin),
                     stdout=sys.stdout,
                     stderr=sys.stderr,
                     env=kwarg.get('env'),
                     shell=kwarg.get('shell', False))

        rc = proc.wait()

        if proc.wait() != 0:
            return False

        return True

    def run_mysql(self, filename):
        sql_fd = open(filename)

        args = ['mysql',
                '--line-numbers',
                '-v',
                '-u%s' % db_config.user,
                '-p%s' % db_config.password,
                db_config.name
                ]

        if db_config.host:
            args.append('-h%s' % db_config.host)

        return self.popen(*args, stdin=sql_fd)

    def run_pgsql(self, filename):
        args = ['psql', '-1', '-a', '-v',
                '-d', db_config.name,
                '-f', filename,
                '--set', 'ON_ERROR_STOP=ON']
        if db_config.user:
            args += ['-U', db_config.user]

        if db_config.host:
            args.append('-h')
            args.append(db_config.host)

        env = deepcopy(os.environ)
        if db_config.password:
            env['PGPASSWORD'] = db_config.password

        return self.popen(*args, env=env)

    def run_shell(self, filename):
        print "* ...run Shell "
        return self.popen(filename, shell=True)

    def run_python(self, filename):
        print "* ...run Python "
        module = imp.load_source('main', filename)
        return module.main()

    def run_sql(self, filename):
        print "* ...run SQL "
        if db_config.engine.startswith('postgresql') \
               or db_config.engine.startswith('postgis'):
            return self.run_pgsql(filename)
        elif db_config.engine.startswith('mysql'):
            return self.run_mysql(filename)
        else:
            raise NotImplementedError("Database driver for %s "\
                                      "not implemented" % db_config.engine)

    @transaction.commit_manually
    def set_applied_patch(self, num, filename):
        exec_sql_modify('insert into db_patch_log (stamp, num, patch) '\
                        'values (%s,%s,%s);',
                        [datetime.now(),
                         num,
                         os.path.basename(filename)])

        transaction.commit()

    @transaction.commit_manually
    def revert_applied_patch(self, num, filename):
        exec_sql_modify('delete from db_patch_log where num = %s',
                        [num])

        transaction.commit()

    def run(self, num, filename):
        short_name = os.path.basename(filename)
        print "\n"
        print "=" * 80
        print "= Run patch %d (%s)" % (num or '', short_name)
        print "=" * 80
        extension = os.path.splitext(filename)[1]

        EXT_MAP = {
            '.sql': self.run_sql,
            '.sh': self.run_shell,
            '.py': self.run_python,
            '.php': self.run_shell,
            }

        handler = EXT_MAP.get(extension)
        if not handler:
            raise NotImplementedError("Handler for filename/extension "\
                                      "%s not implemented" % filename)

        start = datetime.now()
        if handler(filename):
            if num:
                # tearDown.py not has number
                self.set_applied_patch(num, filename)
            print "\n> Success (%s)" % (datetime.now() - start)
            return True
        else:
            print " Error while apply"
            return False


def is_patchnum_applied(num):
    if num:
        return exec_sql("select num from db_patch_log where num=%s" % num)
    else:
        return False



def correct_filename_ext(f):
    for ext in VALID_FILENAME_EXTENSIONS:
        if f.endswith(ext):
            return True
    for ext in IGNORE_EXTENSIONS:
        if f.endswith(ext):
            return False
    print 'Skipped filename with invalid extension: %s' % f
    return False


def get_patch_list(patch_root, skip_reserved=True, silent=False):
    """
    Return ordered list of all files.
    List item content list of 2 elements: patch_number and full file name
    """

    target = {}
    all_targets = {}

    for f in os.listdir(patch_root):
        if not correct_filename_ext(f):
            continue

        patch_no = get_patch_number_by_filename(f)

        if not patch_no:
            continue

        if os.stat(os.path.join(patch_root, f))[stat.ST_SIZE] == 0:
            if not silent:
                print '* Reserved patch for future use: %s' % f
            if skip_reserved:
                continue

        if skip_reserved and patch_no in all_targets:
            print '\nWarning! %s -- This patch number '\
                  'already used in: %s\n' % (f, all_targets[patch_no])
            all_targets[patch_no] = f
            continue
        target[patch_no] = patch_root + f

    pathch_list = target.keys()
    pathch_list.sort()

    target_list = []
    for patch_no in pathch_list:
        target_list.append((patch_no, target[patch_no]))

    if os.path.exists(patch_root + "tearDown.py"):
        target_list.append((None, patch_root + "tearDown.py"))

    return target_list


def get_max_patch_no():
    existing_patches = get_patch_list(_patch_root_dir(), False, True)
    if existing_patches:
        return max(existing_patches)[0]
    else:
        return 0



def lookup_patch_by_number(patch_list, patch_number):
    """
    Return pair (number, filename) by patch_number.
    If patch not found - return None

    """
    for num, filename in patch_list:
        if (num == patch_number):
            return (num, filename)
        if (atoi(patch_number) == atoi(num)):
            return (num, filename)


class Command(LabelCommand):
    help = ("incremental database updater")
    args = '\n\tinstall'
    args += '\n\tup|skip|revert [num]'
    args += '\n\treserve <num>'
    args += '\n\tset_applied <num>'
    args += '\n\tnext'
    args += '\n\tlist'
    commands = ('install', 'up', 'skip', 'revert', 'reserve', 'list',
                'next', 'set_applied')

    requires_model_validation = False
    option_list = LabelCommand.option_list + (
        make_option('-f', '--force',  action='store_true', dest='force',
                    default=False, help='force selected action'),
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.executor = Executor()

    def build_list(self, args, force=False):
        #print 'build list', args, force
        todo_prepare = get_patch_list(_patch_root_dir())
        todo = []
        if len(args):
            for num in args:
                patch_num = atoi(num)
                if not patch_num:
                    print "Warning: %s not is a valid "\
                          "patch number, skipped" % num
                    continue
                patch = lookup_patch_by_number(todo_prepare, patch_num)
                if not patch:
                    print "Warning: %s not found in "\
                          "list of patches, skipped" % num
                    continue

                if not force and is_patchnum_applied(patch[0]):
                    print "Warning: %s patch is allready applied, "\
                          "skipped. (Use -f to force apply)" % num
                    continue

                todo.append(patch)
        else:
            for (num, filename) in todo_prepare:
                #print is_patchnum_applied(num), num
                if force or not is_patchnum_applied(num):
                    todo.append((num, filename))
        return todo

    def handle(self, *args, **options):
        check_depricated()

        if not len(args) or args[0] not in self.commands:
            raise CommandError(
                'Enter one of valid commands %s' % ", ".join(self.commands))
        command = args[0]

        if hasattr(self, 'handle_%s' % command):
            cb = getattr(self, 'handle_%s' % command)
            return cb(*args[1:], **options)

        raise CommandError('Command %s not implemented' % command)

    @transaction.commit_manually
    def handle_install(self, *args, **options):
        print "Install"
        exec_sql("""CREATE TABLE db_patch_log (
                                 stamp timestamp NOT NULL,
                                 patch varchar(255) default NULL,
                                 num integer NOT NULL unique)""")
        transaction.commit()
        print "\tSuccess"

    def handle_skip(self, *args, **options):
        print "Skip patches"
        todo = self.build_list(args, options['force'])

        if not len(todo):
            print "Nothing to skip"
        else:
            print "\nSkip list:"
            for (num, filename) in todo:
                print num, os.path.basename(filename)

            for (num, filename) in todo:
                self.executor.set_applied_patch(int(num), filename)
        print "\t Done."

    def handle_list(self, *args, **options):
        print "List of patches for apply:"
        todo = self.build_list(args, options['force'])

        if not len(todo):
            print "Nothing to apply"
        else:
            for (num, filename) in todo:
                print num, os.path.basename(filename)
        print "\t Done."


    def handle_next(self, *args, **options):
        self.handle_reserve(short_number(get_max_patch_no())+1)


    def handle_up(self, *args, **options):
        start = datetime.now()
        print "Database update"
        print "+++start %s\n" % datetime.now()

        todo = self.build_list(args, options['force'])

        if not len(todo):
            print "Nothing to update"
        else:
            print "\nTodo schedule list:"
            for (num, filename) in todo:
                print num, os.path.basename(filename)

            for (num, filename) in todo:
                if not self.executor.run(int(num), filename):
                    break

        end = datetime.now()
        print "\n+++stop: %s" % end
        print "\telapsed time: %s" % (end - start)

    def handle_reserve(self, *args, **options):
        if not len(args):
            print "Error: specify at least one patch number to be reserved"
            return
        todo_prepare = get_patch_list(_patch_root_dir(), False)
        created = []
        for num in args:
            patch_num = atoi(num)
            if not patch_num:
                print "Warning: %s not is a "\
                      "valid patch number, skipped" % num
                continue

            patch = lookup_patch_by_number(todo_prepare, patch_num)
            if patch:
                print "Warning: %s found in list of patches, skipped." % num
                continue
            newfile = _patch_root_dir() + get_filename_by_number(num)
            open(newfile, "w")
            print "Zero sized patch '%s' has been created." % newfile
        print "\t Done."

    def handle_set_applied(self, *args, **options):
        if not len(args):
            print "Error: specify at least one patch number to be reserved"
            return
        todo_prepare = get_patch_list(_patch_root_dir(), False)
        for num in args:
            patch_num = atoi(num)
            if not patch_num:
                print "Error: %s not is a "\
                      "valid patch number, skipped" % num
                continue

            if is_patchnum_applied(patch_num):
                print "Error: %s already recorded as being applied, skipped." % patch_num
                continue

            self.executor.set_applied_patch(int(patch_num), dict(todo_prepare)[patch_num])

        print "-> set_applied=%s: Finished." % patch_num


    def handle_revert(self, *args, **options):
        print "Revert patches"
        todo = self.build_list(args, True)

        if not len(todo):
            print "Nothing to revert"
        else:
            print "\nRevert list:"
            for (num, filename) in todo:
                print num, os.path.basename(filename)

            for (num, filename) in todo:
                self.executor.revert_applied_patch(int(num), filename)
        print "\t Done."
