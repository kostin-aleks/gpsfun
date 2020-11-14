from __future__ import with_statement
import redis
from datetime import datetime
from django.conf import settings
import json


class RedisConn(object):
    def __init__(self):
        self.conn = None

    def __enter__(self):
        self.conn = redis.Redis(host=settings.REDIS_HOST,
                                port=settings.REDIS_PORT,
                                db=settings.REDIS_DATABASE,
                                password=settings.REDIS_PASSWORD)
        return self.conn

    def __exit__(self, type, value, tb):

        version = getattr(redis, "__version__", (0, 0, 0))
        if version:
            VERSION = tuple(version.split("."))
        else:
            VERSION =redis.VERSION
        if self.conn:
            if (int(VERSION[0])==2 and int(VERSION[1])>=4) or \
                   int(VERSION[0]) > 2:
                self.conn.connection_pool.disconnect()
            else:
                self.conn.connection.disconnect()


def fix_event(event):
    with RedisConn() as r:
        r.zincrby('fix_events', event)


def get_event_count(event):
    with RedisConn() as r:
        return r.zscore('fix_events', event)


def fix_event_month(event):
    """ fix event in current month """
    d = datetime.now()
    with RedisConn() as r:
        r.incr('event.month:%04d.%02d:%s' % (d.year, d.month, event))


def get_event_month_count(event, year, month):
    """ return event count in the month """
    with RedisConn() as r:
        return r.get('event.month:%04d.%02d:%s' % (year, month, event))


def zstore_structure(formset_fact,
                     key,
                     request):

    """ Stores any formset structure into Redis
    sorted set object by `key`.

    Usage example:
        formset = redis_utils.zstore_structure(formset_factory(SomeForm,
                                                           extra=1,
                                                           can_order=True,
                                                           can_delete=True),
                                           REDIS_KEY,
                                           request)
    """

    any_deleted = any_updated = False
    if request.method == 'POST':
        formset = formset_fact(request.POST, request.FILES)
        i = 0
        if formset.is_valid():
            with RedisConn() as rds:
                for form in formset.ordered_forms + formset.deleted_forms:
                    data = form.cleaned_data
                    delete_record = data['DELETE']
                    del data['DELETE']
                    serialized = json.dumps(data)
                    if delete_record:
                        rds.zrem(key, serialized)
                        any_deleted = True
                    else:
                        any_updated = True
                        rds.zadd(key, serialized, i)
                        i += 1

    if not request.method == 'POST' or \
           request.method == 'POST' and \
           (any_updated or any_deleted):
        initial = []
        with RedisConn() as rds:
            for record in rds.zrange(key, 0, -1):
                initial.append(json.loads(record))
        formset = formset_fact(initial=initial)

    return formset

def zdataset(key):
    d=[]
    with RedisConn() as rds:
        for record in rds.zrange(key, 0, -1) or []:
            d.append(json.loads(record))
    return d



class NonParallelLockException(Exception):
    """ Lock is already busy"""
    pass


def non_parallel(name='', timeout=60, quiet_exit=False):
    """ decorator: execute process single (among name namespace)
        (lock by django's redis lock).

        Params:
          name - name of lock namespace
          timeout - lifetime of lock
          quiet_exit - exit in case of NonParallelLockException quietly

        Any parallel execution attempts will be failed
        with NonParallelLockException """

    def decorator(func):
        def newfunc(*args, **kwargs):
            with RedisConn() as redis:
                lock = redis.lock('lock_np_{0}'.format(name), timeout=timeout)

                if lock.acquire(blocking=False):
                    try:
                        return func(*args, **kwargs)
                    finally:
                        lock.release()
                else:
                    error = 'Cannot acquire lock {0}'.format(name)
                    if quiet_exit:
                        print(error)
                    else:
                        raise NonParallelLockException(error)

        return newfunc

    return decorator
