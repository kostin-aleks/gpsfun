from django.db import connection
from django.shortcuts import _get_queryset


def get_cursor(sql, sql_args=None):
    cursor = connection.cursor()
    if sql_args:
        cursor.execute(sql, sql_args)
    else:
        cursor.execute(sql)
    return cursor


def sql2list(sql, sql_args=None):
    cursor = get_cursor(sql, sql_args)
    row = cursor.fetchone()
    return row


def sql2val(sql, sql_args=None):
    cursor = get_cursor(sql, sql_args)
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return None


def sql2table(sql, sql_args=None):
    cursor = get_cursor(sql, sql_args)
    items = []
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        else:
            items.append(row)
    return items


def sql_col2str(sql, col=0, sql_args=None):
    cursor = get_cursor(sql, sql_args)
    items = []
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        else:
            items.append(str(row[col]))
    return ','.join(items)


def sql2col(sql, col=0, sql_args=None):
    cursor = get_cursor(sql, sql_args)
    items = []
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        else:
            items.append(row[col])
    return items


def dictionary_list_from_tuple_list(items, columns_tuple):
    if type(items) == type((1, )):
        items = [items, ]
    lst = []
    if len(items) and len(columns_tuple):
        for item_tuple in items:
            d = {}
            if len(item_tuple) and (len(item_tuple) == len(columns_tuple)):
                for item in zip(columns_tuple, item_tuple):
                    d[item[0]] = item[1]
            lst.append(d)
    return lst


def execute_query(sql, sql_args=None):
    cursor = connection.cursor()
    if sql_args:
        cursor.execute(sql, sql_args)
    else:
        cursor.execute(sql)

    return True


def get_object_or_none(klass, *args, **kwargs):
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None

