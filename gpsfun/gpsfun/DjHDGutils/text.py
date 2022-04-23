#!/usr/bin/env python
"""
text
"""

import string


def ru_trans(test_str):
    test_str = test_str.encode('cp1251')
    tbl = string.maketrans(
        'абвгдеёжзийклмнопрстуфхцчшщьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЭЮЯ'.encode('1251'),
        'abvgdeegzijklmnoprstufhcchhieujabvgdeegzijklmnoprstufhcchhieuj')
    return test_str.translate(tbl).decode('cp1251').encode('utf-8')
