import os
import json
import warnings
from urlparse import urlparse
from copy import deepcopy

from django.test import TestCase as DjangoTestCase
from django.test.runner import DiscoverRunner
from django.db import connections, DEFAULT_DB_ALIAS
from django.test.client import Client, MULTIPART_CONTENT


def chrome_debug(response):
    tmpname = '/tmp/%d-debug.html' % os.getpid()
    open(tmpname, 'w').write(response.content)
    from DjHDGutils.shell_utils import startprocess
    startprocess("chromium " + tmpname)


class DefaultDatabaseRunner(DiscoverRunner):
    """
    Run all tests in default database
    Compatibility 1.3.x Django
    Usage:
    write in settings.py:
    TEST_RUNNER = 'DjHDGutils.testutils.DefaultDatabaseRunner'
    """
    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass


class TestCase(DjangoTestCase):
    """ This custom test case skips database cleanup before running """

    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)
        self._client = Client()
        self._response = None
        self._last_url = None
        self._soup = None
        self._lxml_doc = None

    # improved Django functions
    def _fixture_setup(self):
        if getattr(self, 'multi_db', False):
            databases = connections
        else:
            databases = [DEFAULT_DB_ALIAS]

    def _post_teardown(self):
        """ Performs any post-test things. This includes:

            * Putting back the original ROOT_URLCONF if it was changed.
        """
        self._urlconf_teardown()

    def get(self, *args, **kwargs):
        self._last_url = args[0]
        self._response = self._client.get(*args, **kwargs)
        self._soup = None
        self._lxml_doc = None

    def post_url(self, path, data={}, content_type=MULTIPART_CONTENT,
                 follow=False, **extra):
        self._last_url = path
        self._response = self._client.post(path, data,
                                           content_type,
                                           follow, **extra)
        self._soup = None

    def post(self, data={}, content_type=MULTIPART_CONTENT,
             follow=False, **extra):

        self.post_url(self.url, data, content_type,
                      follow, **extra)

    def assertContains(self, text, count=None, status_code=200,
                       msg_prefix=''):
        super(TestCase, self).assertContains(self._response,
                                             text=text,
                                             count=count,
                                             status_code=status_code,
                                             msg_prefix=msg_prefix)

    def assertNotContains(self, text, status_code=200,
                          msg_prefix=''):
        super(TestCase, self).assertNotContains(self._response,
                                                text=text,
                                                status_code=status_code,
                                                msg_prefix=msg_prefix)

    # our own related function
    @property
    def soup(self):
        """ parse HTML doc and return BeautifulSoup document """
        from BeautifulSoup import BeautifulSoup
        warnings.warn("the use of BeautifulSoup is deprecated, use html5lib "
                      "or lxml instead", DeprecationWarning)

        if not self._soup:
            self._soup = BeautifulSoup(self.text)
        return self._soup

    @property
    def lxml_doc(self):
        """ parse HTML doc and return lxml document """
        import lxml.html
        if not self._lxml_doc:
            self._lxml_doc = lxml.html.document_fromstring(
                self.text)
        return self._lxml_doc

    # twill related functions
    @property
    def url(self):
        if hasattr(self._response, 'redirect_chain') \
           and self._response.redirect_chain:
            return self._response.redirect_chain[-1][0]
        return self._last_url

    @property
    def text(self):
        return self._response.content

    def response_code(self):
        return self._response.status_code

    def assertCode(self, code):
        self.assertEquals(code, self._response.status_code)

    def follow(self):
        raise 'TODO: Implement'

    def find(self, text):
        self.assertContains(text)

    # def ff(self):
    #     """ show current page in browser """
    #     chrome_debug(self._response)

    def ajax_on(self):
        self._client.defaults['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'

    def ajax_off(self):
        if 'HTTP_X_REQUESTED_WITH' in self._client.defaults:
            del self._client.defaults['HTTP_X_REQUESTED_WITH']

    def json(self):
        return json.loads(self.text)


class HostsRequestFactory(Client, object):
    """
    This ClientFactory should use with django_hosts extention to proper handling
    request for different hosts
    """
    def _update_env(self, path, extra):
        parsed = urlparse(path)

        kwargs = deepcopy(extra)
        kwargs['HTTP_HOST'] = parsed.netloc
        return kwargs

    def get(self, path, data={}, follow=False, **extra):
        return super(HostsRequestFactory, self).get(path,
                                                    data,
                                                    follow,
                                                    **self._update_env(path, extra))

    def post(self, path, data={}, content_type=MULTIPART_CONTENT, follow=False, **extra):
        return super(HostsRequestFactory, self).post(path,
                                                     data,
                                                     content_type,
                                                     follow,
                                                     **self._update_env(path, extra))

    def head(self, path, data={}, follow=False, **extra):
        return super(HostsRequestFactory, self).head(path,
                                                     data,
                                                     follow,
                                                     **self._update_env(path, extra))

    def options(self, path, data={}, follow=False, **extra):
        return super(HostsRequestFactory, self).options(path,
                                                        data,
                                                        follow,
                                                        **self._update_env(path, extra))

    def put(self, path, data={}, content_type=MULTIPART_CONTENT,
            follow=False, **extra):
        return super(HostsRequestFactory, self).put(path,
                                                    data,
                                                    content_type,
                                                    follow,
                                                    **self._update_env(path, extra))

    def delete(self, path, data={}, follow=False, **extra):
        return super(HostsRequestFactory, self).delete(path,
                                                       data,
                                                       follow,
                                                       **self._update_env(path, extra))
