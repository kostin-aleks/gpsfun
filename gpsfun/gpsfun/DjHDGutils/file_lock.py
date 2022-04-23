#!/usr/bin/env python
""" Simple lock operations based on temporary file locks """
# TODO: improve to use tempfile module

from django.core.files import locks
from time import sleep
import os


FILE_NAME_PREFIX = f'/tmp/file_lock_{os.getuid()}_'


class LockException(Exception):
    """ Resourse is locked """
    pass


def get_lock(name, timeout='forewer'):
    """ Acquire and return unique lock (locked file)
    If lock has not been created before timeout then IOError raised """

    f = open(FILE_NAME_PREFIX + name, 'wb')

    if timeout == 'forewer':
        locks.lock(f, locks.LOCK_EX)
    else:
        # print '   waiting for lock...'
        for waited in range(timeout + 1):
            try:
                if waited > 0:         # sleep between iterations
                    sleep(1)
                locks.lock(f, locks.LOCK_EX + locks.LOCK_NB)
                break
            except IOError:
                pass
        else:
            f.close()
            raise LockException('Get lock timeout')

    return f


def unlock(lock):
    """ release lock (unlock locked file) """

    locks.unlock(lock)


# decorator
def single_execute(lock_name, timeout=0, quiet_exit=False):
    """ Execute decorated function and deny to execute any parallel
        same-decorated function until execution finish.

        Params:
          lock_name - name of single-executed functions group.
          timeout - seconds the parallel process wait until executing process
                    finish. When exceeded then IOError raised.
                    Can also have 'forewer' value instead of integer.
          quiet_exit - exit in case of LockException without exception

        Can decorate different functions with same lock_name.

    """

    def f1(f):
        """ f1 """
        def f2(*args, **kwargs):
            """ f2 """
            try:
                _lock = get_lock('single_execute_lock_%s' % lock_name,
                                 timeout=timeout)

                try:
                    return f(*args, **kwargs)
                finally:
                    unlock(_lock)

            except LockException:
                if quiet_exit:
                    print('Cannot acquire lock {0}'.format(lock_name))
                    return
                else:
                    raise

        return f2
    return f1
