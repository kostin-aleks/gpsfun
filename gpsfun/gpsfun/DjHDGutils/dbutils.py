import re
import os

import django
from django.db import connection, models
from django.shortcuts import _get_queryset
from django.conf import settings
from django.db import transaction

from .execution import shellcmd


"""
Compatibility layer for transparent using Django <1.2 and >-1.3

Note:
Structure of django database config was changed.
New django config allow work with several databases.

Classes below provide compatibility layer for DjHDGutils

"""

class DjangoDb(object):
    name = None
    host = None
    password = None
    user = None
    engine = None
    port = None

    def cmdargs(self):
        args = ''
        if self.engine.endswith('postgresql_psycopg2'):
            if self.host:
                args += ' -h %s' % self.host
            if self.password:
                os.environ['PGPASSWORD'] = self.password
            if self.user:
                args += ' -U %s' % self.user
            if self.port:
                args += ' -p %s' % self.port
            if self.name:
                args += ' -d %s' % self.name
        elif self.engine.endswith('mysql'):
            if self.host:
                args += ' -h  %s' % self.host
            if self.password:
                args += ' -p"%s"' % self.password
            if self.user:
                args += ' -u%s' % self.user
            if self.name:
                args += ' %s' % self.name
            if self.port:
                args += ' -p %s' % self.port
        else:
            raise ValueError('%s engine is not yet supported' % db_config.engine)
        return args

    def as_dict(self):
        return dict(NAME = self.name,
                    HOST = self.host,
                    PASSWORD = self.password,
                    USER = self.user,
                    ENGING = self.engine,
                    PORT = self.port)


class NewDjangoDb(DjangoDb):
    def __init__(self, database='default'):
        self.name = settings.DATABASES[database]['NAME']
        self.host = settings.DATABASES[database].get('HOST')
        self.port = settings.DATABASES[database].get('PORT')
        self.user = settings.DATABASES[database]['USER']
        self.password = settings.DATABASES[database].get('PASSWORD')
        self.engine = settings.DATABASES[database]['ENGINE'].split('.')[-1]

class OldDjangoDb(DjangoDb):
    def __init__(self):
        self.name = settings.DATABASE_NAME
        self.host = settings.DATABASE_HOST
        self.port = settings.DATABASE_PORT
        self.user = settings.DATABASE_USER
        self.password = settings.DATABASE_PASSWORD
        self.engine = settings.DATABASE_ENGINE


def get_db_config(database='default'):
    if hasattr(settings, 'DATABASES'):
        db_config = NewDjangoDb(database)
    else:
        db_config = OldDjangoDb()
    return db_config

db_config = get_db_config()


def get_object_or_none(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


def escape(value):
    return re.sub(r'([\\\'\"])', r'\\\1', value)


def exec_sql(sql,args=[], database='default'):
    if database!='default':
        from django.db import connections
        cursor = connections[database].cursor()
    else:
        cursor = connection.cursor()
    cursor.execute(sql,args)

    if cursor.rowcount > 0:
        row = cursor.fetchone()
    else:
        row = None

    cursor.close()
    return row


def exec_sql_modify(sql, args=[]):
    cursor = connection.cursor()

    if hasattr(cursor, 'Warning'):
        """ compatibility with MySQL """
        try:
            cursor.execute(sql,args)
        except cursor.Warning:
            pass
    else:
        cursor.execute(sql,args)


    rc = cursor.rowcount
    cursor.close()
    return rc


def iter_sql(sql, args=[], database='default'):
    if database!='default':
        from django.db import connections
        cursor = connections[database].cursor()
    else:
        cursor = connection.cursor()

    cursor.execute(sql,args)

    while True:
        row = cursor.fetchone()
        if row is None:
            break
        yield row
    cursor.close()



def set_sequence(model, value):
    curs = connection.cursor()
    sql = "select setval('%s_%s_seq',%%s);"%(model._meta.db_table, model._meta.pk.column)
    curs.execute(sql,(value+1,))

def get_max_pk(model):
    """
    Return max value of pk column
    """
    sql = "select max(%s) from %s;"%(model._meta.pk.column, model._meta.db_table)
    row = exec_sql(sql)
    return row[0]


#FIXME: (Vic) here not perfect way to detect django version.
#       Requere to move out MySQLSequence to standalone file

if 'unknown' not in django.get_version() and \
       (('-' in django.get_version() and int(django.get_version().split('-')[-1])>7476) or \
   ('-' not in django.get_version() and int(django.get_version().split('.')[0]) >= 1)):

    class MySQLSequence(models.Model):
        id = models.IntegerField(primary_key=True, default=0)

        def next(self):
            cursor = connection.cursor()
            cursor.execute("UPDATE %s SET id=LAST_INSERT_ID(id+1)" % self._meta.db_table)
            if cursor.rowcount == 0:
                cursor.execute("INSERT INTO %s VALUES (0)" % self._meta.db_table)

            cursor.execute("SELECT LAST_INSERT_ID();")

            return cursor.fetchall()[0][0]

        class Meta:
            abstract=True


    class PgSQLSequence(models.Model):
        class Meta:
            abstract=True

        @classmethod
        def next(cls):
            from django.db import connections, transaction
            connection = connections['default']
            cursor = connection.cursor()
            cursor.execute("SELECT NEXTVAL(pg_get_serial_sequence('%s','%s'))" % (
                connection.ops.quote_name(cls._meta.db_table), cls._meta.pk.name))
            return cursor.fetchone()[0]



def drop_create_database(use_superuser=False, database='default'):
    db_config = get_db_config(database)
    if db_config.engine in ('postgresql_psycopg2', 'postgis'):
        import psycopg2
        if use_superuser:
            params = "dbname='template1' user='postgres'"
        else:
            params = "dbname='template1' user='%(user)s'" % dict(user = db_config.user)
        if db_config.host:
            params += "host='%s'" % db_config.host
        if db_config.password:
            params += "password='%s'" % db_config.password
        conn = psycopg2.connect(params)
        conn.set_isolation_level(0) # To drop the database you would need to change the isolation level
        cursor = conn.cursor()
        try:
            cursor.execute('drop database "%s"' % db_config.name)
        except psycopg2.ProgrammingError:
            pass

        create_cmd = 'create database "%s"' % db_config.name
        if db_config.user:
            create_cmd += ' owner "%s"' % db_config.user
        cursor.execute(create_cmd)
        cursor.close()
        conn.close()

    elif db_config.engine == 'mysql':
        shellcmd("echo drop database IF EXISTS \`%s\`  \; "\
                 "create database %s | mysql -u%s -p%s" % (db_config.name,
                                                           db_config.name,
                                                           db_config.user,
                                                           db_config.password))

    elif db_config.engine == 'sqlite3':
        dbfilename = os.path.join(settings.SITE_ROOT, db_config.name)
        if os.path.exists(dbfilename):
            os.unlink(dbfilename)
    else:
        raise ValueError(
            'Database engine %s is not supported by reinst_db.py script' % \
            settings.DATABASE_ENGINE)


class reg(object):
    """ http://code.activestate.com/recipes/577186-accessing-cursors-by-field-name/ """
    def __init__(self, cursor, row):
        for (attr, val) in zip((d[0] for d in cursor.description), row) :
            setattr(self, attr, val)


class LockForUpate(object):
    def _raw_lock(self):
        cursor = connection.cursor()
        cursor.execute("""select id from \"%s\" where id=%%s for update""" % self._meta.db_table,
                       [self.id])
        row = cursor.fetchone()
        cursor.close()
        return type(self).objects.get(pk=self.id)

    def _native_lock(self):
        return type(self).objects.select_for_update().get(pk=self.id)

    def lock_for_update(self):
        """
        lock object for update
        Return locked object

        """
        if hasattr(self._base_manager, 'select_for_update'):
            return self._native_lock()

        return self._raw_lock()


def update_diff(instanse, **kwargs):
    need_save = False

    for key, value in kwargs.iteritems():
        field = getattr(instanse, key)
        if field != value:
            setattr(instanse, key, value)
            need_save = True

    if need_save:
        instanse.save()
    return need_save


def exec_sql_modify_many(sql, args=[]):
    cursor = connection.cursor()

    if hasattr(cursor, 'Warning'):
        """ compatibility with MySQL """
        try:
            cursor.executemany(sql,args)
        except cursor.Warning:
            pass
    else:
        cursor.executemany(sql,args)


    rc = cursor.rowcount
    cursor.close()
    return rc
