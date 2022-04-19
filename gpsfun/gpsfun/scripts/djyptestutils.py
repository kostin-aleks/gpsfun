"""
djyp test utils
"""

import os
import re
import urllib
from datetime import datetime, timedelta
from twill import commands as cmd
from twill.namespaces import get_twill_glocals
from twill.errors import TwillAssertionError
from bs4 import BeautifulSoup


TEST_TEACHER_LOGIN = 'test_teacher'
TEST_TEACHER_PASSWD = 'test'
TEST_STUDENT_LOGIN = 'test_student'
TEST_STUDENT_PASSWD = 'test'
TEST_STUDENTSET = 'test_studentset'


test_dir = os.path.dirname(os.path.abspath(__file__))
SITE_ROOT = os.path.normpath(os.path.join(test_dir, '../..'))

BIG_DATE = datetime(2020, 1, 1, 1, 1)


def admin_date(stamp):
    """ used in django admin for datetime values """
    return stamp.strftime("%Y-%m-%d")

def admin_time(stamp):
    """ format time string """
    return stamp.strftime("%H:%M:%S")


def current_second():
    """ return unique number for current second """
    return datetime.now().strftime('%Y%M%d%H%M%S')

def uniq():
    """ return current seconds """
    return current_second()


def firefox():
    """ show current page in firefox """

    # if not os.environ.get('DEBUG_TEST', False):
    #     return

    # turn on debugging to show
    # set_debugging(True)

    filename = f'/tmp/_yp_test_{uniq()}'  # os.tmpnam() make warnings

    with open(filename, 'w') as f:
        html = cmd.show()

        # replace home urls to htdocs dir urls
        html = html.replace('"/', f'"{SITE_ROOT}/htdocs/')

        html = html.replace('url(/', f'url({SITE_ROOT}/htdocs/')

        # delete rX for css version
        for revision in range(7, 50):
            html = html.replace(f'/r{revision}/', '/')

        f.write(html)
        f.close()
    os.system(f'/usr/bin/env firefox {filename}')


SITE = os.environ.get('YP_HOSTNAME')


def set_up():
    """ set up """
    cmd.clear_cookies()


def safe_browser(f):
    """ decorator: call function with independent twill browser """

    def tmp(*args, **kwargs):
        """ tmp """
        old_browser = cmd.browser
        try:
            cmd.browser = cmd.TwillBrowser()
            set_up()
            return f(*args, **kwargs)
        finally:
            cmd.browser = old_browser

    return tmp


def admin_browser(f):
    """ decorator: call function in 'admin browser' """
    def tmp(*args, **kwargs):
        old_browser = cmd.browser
        try:
            cmd.browser = _admin_browser
            # ? no! set_up()
            return f(*args, **kwargs)
        finally:
            cmd.browser = old_browser

    return tmp


def safe_url(f):
    """ decorator: call function with current url restoring """

    def tmp(*args, **kwargs):
        """ tmp """
        old_url = cmd.get_browser().get_url()
        try:
            return f(*args, **kwargs)
        finally:
            cmd.go(old_url)

    return tmp


def get(url):
    """ get """
    cmd.go(url)
    try:
        cmd.code(200)
    except TwillAssertionError as error:
        firefox()
        raise TwillAssertionError(f'{error} url {fullurl(url)}')


def post(url, data):
    """ POST data to url (using twill) """
    browser = cmd.get_browser()
    mbrowser = browser._browser
    result = mbrowser.open(url, urllib.urlencode(data))
    return result


def post3(url, **post_kwargs):
    """ post3 """
    post2(url, data=post_kwargs)


def follow_anchor_by_name(text):
    """ sometimes follow not works somewhy. This is simplified equivalent """
    href = soup().find('a', text=text).parent['href']
    cmd.go(href)


def _soup(html):
    """ retutn soup of html """
    return BeautifulSoup(html)


def soup(code_page='cp1251'):
    """ return soup based on current twill html """
    return _soup(unicode(cmd.show(), code_page).encode('utf8'))


def get_local(name, default=None):
    """ return twill Local's variable value """

    gvars, lvars = get_twill_glocals()
    return lvars.get(name, default)


def find_re(reg, tag=None):
    """
    find re inside tag and return list of re-groups

    if tag=None then search through all html.
    """

    tag = tag or soup()

    result = re.compile(reg)
    text = tag.find(text=result)
    return result.search(text).groups()


def find_cross_td(table_id, row_text, col_text):
    """ return td soup tag on crossroad of table col_text and row_text """

    table = soup().find('table', id=table_id)

    column_index = [i
                    for i, th in enumerate(table.findAll('th'))
                    if th.string == col_text][0]

    row = [tr for tr in table.findAll('tr')if tr.fetchText(row_text)][0]

    cell = row.findAll('td', limit=column_index+1)[-1]

    return cell


TEST_AGROUP_NAME = 'test_agroup'

def set_cookie(domain, name, value, expires=(datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")):
    """ idea from http://www.mail-archive.com/twill@lists.idyll.org/msg00951.html """
    cookie_file = "cookies.txt"

    params = dict(domain=domain,
                  name=name,
                  value=value,
                  expires=expires)

    cmd.save_cookies(cookie_file)
    with open(cookie_file, "a+") as cookie:
        cookie.write('Set-Cookie3: %(name)s=%(value)s; '\
                     'path="/"; domain="%(domain)s"; path_spec; domain_dot; '\
                     'expires="%(expires)s"; version=0' % params)
        cookie.flush()
        cmd.load_cookies(cookie_file)
        os.unlink(cookie_file)
