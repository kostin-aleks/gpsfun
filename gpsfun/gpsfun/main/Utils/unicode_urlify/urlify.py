"""
urlify
"""

import re
from .maps import (
    latin_map, latin_symbol_map, greek_map, turkish_map, russian_map,
    ukrainian_map, czech_map, polish_map, latvian_map)


western_maps = [latin_map, latin_symbol_map, greek_map, turkish_map,
                russian_map, ukrainian_map, czech_map, polish_map, latvian_map]

for map_ in western_maps:
    map_ = dict([(ord(k), v) for k, v in map_.items()])

STOP_WORDS = ['a', 'an', 'as', 'at', 'before', 'but', 'by', 'for',
              'from', 'is', 'in', 'into', 'like', 'of', 'off', 'on',
              'onto', 'per', 'since', 'than', 'the', 'this', 'that',
              'to', 'up', 'via', 'with']

RESERVED_WORDS = ['blog', 'edit', 'delete', 'new', 'popular', 'wiki']


def urlify(urlstring, default='default', max_length=50,
           stop_words=None, reserved_words=None):
    """
    urlify some string
    """
    if stop_words is None:
        stop_words = STOP_WORDS
    if reserved_words is None:
        reserved_words = RESERVED_WORDS
    slug = ''
    re_alnum = re.compile(r'[\w\s\-]+')
    re_stop = re.compile('|'.join([f'\b{word}\b' for word in stop_words]))
    re_reserved = re.compile('|'.join([f'\b{word}\b' for word in reserved_words]))
    re_space = re.compile(r'[\s_\-]+')

    for char in urlstring:
        if len(slug) >= max_length:
            break
        if re_alnum.match(char):
            slug += char
            continue
        char_ord = ord(char)
        for wm_dict in western_maps:
            if char_ord in wm_dict:
                slug += wm_dict[char_ord]
                break

    slug = re_stop.sub(u'', slug.lower())
    slug = re_space.sub(u'-', slug.strip())
    if not slug or re_reserved.match(slug):
        slug = default

    return slug
