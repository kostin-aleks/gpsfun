from hashlib import md5

from django.core.cache import cache
from django.core.cache import get_cache
from django.utils.http import urlquote
from functional import compose


def invalidate_template_cache(fragment_name, *variables):
    """ http://djangosnippets.org/snippets/1593/ """
    args = md5(u':'.join(apply(compose(urlquote, unicode), variables)))
    cache_key = 'template.cache.%s.%s' % (fragment_name, args.hexdigest())
    cache.delete(cache_key)

def lazycache_value(key, value_or_func, time_seconds, cache_name='default', *args, **kwargs):
    """ caches lazy function `function` result """
    cache = get_cache(cache_name)
    if callable(value_or_func):
        value = cache.get(key)
        if value is None:
            value = value_or_func(*args, **kwargs)
            cache.set(key, value, time_seconds)
        return value
    else:
        cache.set(key, value_or_func, time_seconds)


def lazycache_invalidate(key):
    """ caches lazy function `function` result """
    value = cache.get(key)
    if value is not None:
        cache.delete(key)
