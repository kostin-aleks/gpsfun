"""
profiling
"""
import hotshot
import os
import time

from django.conf import settings
from django.db import connection
from django.template import Template, Context


class SQLLogMiddleware:
    """
    http://www.djangosnippets.org/snippets/161/

    To enable, add the following line to your settings.py:
    MIDDLEWARE_CLASSES += ('DjHDGutils.profiling.SQLLogMiddleware',)
    """

    def process_response(self, request, response):
        """ process response """

        time = 0.0
        for q in connection.queries:
            time += float(q['time'])

        if response['Content-type'].find('text/html') == -1:
            return response

        t = Template(u'''
                     <p><em>Total query count:</em> {{ count }}<br/>
                     <em>Total execution time:</em> {{ time }}</p>
                     <ul class="sqllog">
                     {% for sql in sqllog %}
                     <li>{{ sql.time }}: {{ sql.sql }}</li>
                     {% endfor %}
                     </ul>
                     ''')

        content = response.content.decode('utf-8')
        content += t.render(Context({'sqllog': connection.queries, 'count': len(connection.queries), 'time': time}))
        response.content = content.encode('utf-8')

        return response

# receoipt from https://code.djangoproject.com/wiki/ProfilingDjango


try:
    PROFILE_LOG_BASE = settings.PROFILE_LOG_BASE
except:
    PROFILE_LOG_BASE = "/tmp"


def profile(log_file):
    """Profile some callable.

    This decorator uses the hotshot profiler to profile some callable (like
    a view function or method) and dumps the profile data somewhere sensible
    for later processing and examination.

    It takes one argument, the profile log name. If it's a relative path, it
    places it under the PROFILE_LOG_BASE. It also inserts a time stamp into the
    file name, such that 'my_view.prof' become 'my_view-20100211T170321.prof',
    where the time stamp is in UTC. This makes it easy to run and compare
    multiple trials.
    """

    if not os.path.isabs(log_file):
        log_file = os.path.join(PROFILE_LOG_BASE, log_file)

    def _outer(f):
        """ outer """
        def _inner(*args, **kwargs):
            """
            Add a timestamp to the profile output when the callable
            is actually called.
            """
            (base, ext) = os.path.splitext(log_file)
            base = base + "-" + time.strftime("%Y%m%dT%H%M%S", time.gmtime())
            final_log_file = base + ext

            prof = hotshot.Profile(final_log_file)
            try:
                ret = prof.runcall(f, *args, **kwargs)
            finally:
                prof.close()
            return ret

        return _inner
    return _outer
