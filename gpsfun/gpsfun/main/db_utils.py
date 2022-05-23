"""
DB utils
"""
from django.db import connection, connections
from django.shortcuts import _get_queryset


def get_cursor(sql, sql_args=None):
    """ get cursor """
    cursor = connection.cursor()
    if sql_args:
        cursor.execute(sql, sql_args)
    else:
        cursor.execute(sql)
    return cursor


def sql2list(sql, sql_args=None):
    """ execute sql query and get result as list of values """
    cursor = get_cursor(sql, sql_args)
    row = cursor.fetchone()
    return row


def sql2val(sql, sql_args=None):
    """ execute sql query and get result as value """
    cursor = get_cursor(sql, sql_args)
    row = cursor.fetchone()
    if row:
        return row[0]
    return None


def sql2table(sql, sql_args=None):
    """ execute sql query and get result as table of values """
    cursor = get_cursor(sql, sql_args)
    items = []
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        items.append(row)
    return items


def sql_col2str(sql, col=0, sql_args=None):
    """ execute sql query and get values """
    cursor = get_cursor(sql, sql_args)
    items = []
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        items.append(str(row[col]))
    return ','.join(items)


def sql2col(sql, col=0, sql_args=None):
    """ execute query and get list of values from the column """
    cursor = get_cursor(sql, sql_args)
    items = []
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        items.append(row[col])
    return items


def dictionary_list_from_tuple_list(items, columns_tuple):
    """ get list of dictionaries from list of tuples """
    if isinstance(items, tuple):
        items = [items]
    lst = []
    if len(items) and len(columns_tuple):
        for item_tuple in items:
            data = {}
            if len(item_tuple) and (len(item_tuple) == len(columns_tuple)):
                for item in zip(columns_tuple, item_tuple):
                    data[item[0]] = item[1]
            lst.append(data)
    return lst


def execute_query(sql, sql_args=None):
    """ execute sql query  with args """
    cursor = connection.cursor()
    if sql_args:
        cursor.execute(sql, sql_args)
    else:
        cursor.execute(sql)

    return True


def get_object_or_none(klass, *args, **kwargs):
    """ get object or None """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


def iter_sql(sql, args=None, database='default'):
    """ iterate sql """
    if args is None:
        args = []
    if database != 'default':
        cursor = connections[database].cursor()
    else:
        cursor = connection.cursor()

    cursor.execute(sql, args)

    while True:
        row = cursor.fetchone()
        if row is None:
            break
        yield row
    cursor.close()
