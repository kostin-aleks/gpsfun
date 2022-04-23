"""
response
"""
from datetime import datetime


def datetime_to_cookie(dt):
    return datetime.strftime(dt, "%a, %d-%b-%Y %H:%M:%S GMT")
