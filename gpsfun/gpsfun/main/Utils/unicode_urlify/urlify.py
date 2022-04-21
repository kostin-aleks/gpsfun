"""
urlify
"""

import re
from maps import *

western_maps = [ latin_map, latin_symbol_map, greek_map, turkish_map, \
                russian_map, ukrainian_map, czech_map, polish_map, latvian_map ]

for i in xrange(len(western_maps)):
    western_maps[i] = dict([(ord(k), v) for k, v in western_maps[i].items()])

stop_words = [u'a', u'an', u'as', u'at', u'before', u'but', u'by', u'for',
              u'from', u'is', u'in', u'into', u'like', u'of', u'off', u'on',
              u'onto', u'per', u'since', u'than', u'the', u'this', u'that',
              u'to', u'up', u'via', u'with']

reserved_words = [u'blog', u'edit', u'delete', u'new', u'popular', u'wiki']


def urlify(urlstring, default='default', max_length=50,
           stop_words=stop_words, reserved_words=reserved_words):
    slug = ''
    re_alnum = re.compile(r'[\w\s\-]+')
    re_stop = re.compile('|'.join([r'\b%s\b' % word for word in stop_words]))
    re_reserved = re.compile('|'.join([r'\b%s\b' % word for word in reserved_words]))
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
    if slug is '' or re_reserved.match(slug):
        slug = default

    return slug
