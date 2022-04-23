"""
sync redmine wiki
"""
import os
import urllib
import urllib2
from HTMLParser import HTMLParser
from collections import namedtuple
import cookielib
import getpass
import hashlib
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand


if hasattr(settings, 'REDMINE_URL'):
    REDMINE_URL = settings.REDMINE_URL
else:
    REDMINE_URL = 'https://tasks.ua2web.com'

if hasattr(settings, 'DOCS_HOME'):
    DOCS_HOME = settings.DOCS_HOME
else:
    DOCS_HOME = settings.SITE_ROOT + 'doc/'

PROJECT_NAME = settings.REDMINE_PROJECT_NAME

WIKI_URL = WIKI_HOME_URL = f"{REDMINE_URL}/projects/{PROJECT_NAME}/wiki/"
WIKI_HOME_URL = WIKI_URL + 'index'

LOGIN_URL_URL = REDMINE_URL + '/login'
METAFILE = 'fileinfo.txt'
FRESH_EXT = '-new'
WIKI_EXT = '.txt'


class LoginFormParser(HTMLParser):
    """ LoginFormParser """

    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.authenticity_token = None

    def handle_starttag(self, tag, attrs):
        """ handle_starttag """
        if tag == 'input':
            for (name, val) in attrs:
                if name == 'name' and val == 'authenticity_token':
                    for (name, val) in attrs:
                        if name == 'value':
                            self.authenticity_token = val


class FeedLinkParser(HTMLParser):
    """ FeedLinkParser """

    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.last_tag = None
        self.atom_url = None

    def handle_starttag(self, tag, attrs):
        """ handle starttag """
        if tag == 'a':
            self.last_tag = tag
            self.last_tag_attrs = attrs

    def handle_data(self, data):
        """ handle data """
        if self.last_tag and self.last_tag == 'a':
            if data == 'Atom':
                for name, value in self.last_tag_attrs:
                    if name == 'href':
                        self.atom_url = value


class WikiPagesParser(HTMLParser):
    """ WikiPagesParser """

    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.last_tag = None
        self.atom_url = None
        self.in_pages_hierarchy = False
        self.last_tag_attrs = None
        self.wiki_pages = []
        self._ul_level = 0

    def handle_starttag(self, tag, attrs):
        """ handle start tag """
        self.last_tag = tag
        if tag == 'ul':
            if ('class', 'pages-hierarchy') in attrs:
                self.in_pages_hierarchy = True
            if self.in_pages_hierarchy:
                self._ul_level += 1

        if tag == 'a' and self.in_pages_hierarchy:
            self.last_tag_attrs = attrs

    def handle_endtag(self, tag):
        """ handle end tag """
        if tag == 'ul':
            if self.in_pages_hierarchy:
                self._ul_level -= 1
            if self._ul_level == 0:
                self.in_pages_hierarchy = False

    def handle_data(self, data):
        """ handle data """
        if self.last_tag == 'a' and self.in_pages_hierarchy:
            if data.strip():
                self.wiki_pages.append((
                    dict(self.last_tag_attrs)['href'],
                    data.strip()))


class WikiEditPageParser(HTMLParser):
    """ WikiEditPageParser """

    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self._in_wiki_edit = False
        self.text = ''
        self._csrf = None
        self.authenticity_token = None
        self.content_version = None

    def handle_starttag(self, tag, attrs):
        """ handle start tag """
        if tag == 'textarea' and ('class', 'wiki-edit') in attrs:
            self._in_wiki_edit = True
        elif tag == 'input':
            if ('name', 'authenticity_token') in attrs:
                for name, value in attrs:
                    if name == 'value':
                        self.authenticity_token = value
            elif ('name', 'content[version]') in attrs:
                for name, value in attrs:
                    if name == 'value':
                        self.content_version = value

    def handle_data(self, data):
        """ handle data """
        if self._in_wiki_edit:
            self.text += data

    def handle_endtag(self, tag):
        """ handle end tag """
        if tag == 'textarea' and self._in_wiki_edit:
            self._in_wiki_edit = False


def main():
    """ main procedure """
    os.chdir(DOCS_HOME)
    cj = cookielib.CookieJar()
    browser = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    login(browser)
    read_from_redmine(browser)
    compared = compare_files()
    process_changes(browser, compared)
    remove_temp_files()


def login(browser):
    """ login """
    while True:
        redmine_name = raw_input('Redmine Username: ')
        redmine_pass = getpass.getpass()

        # --- Open Login Page
        r = browser.open("https://tasks.ua2web.com/login")
        parser = LoginFormParser()
        parser.feed(r.read())
        # print 'auth token:', parser.authenticity_token

        # --- Post Login Form
        data = {}
        data['username'] = redmine_name
        data['password'] = redmine_pass
        data['login'] = 'Login'
        data['authenticity_token'] = parser.authenticity_token
        params = urllib.urlencode(data)
        r = browser.open("https://tasks.ua2web.com/login", params)
        print(f'Logged in to {REDMINE_URL}.')
        if 'Lost password' in r.read():
            print('Wrong login.\n')
            continue
        else:
            break


def read_from_redmine(browser):
    """ read from redmine """
    # --- Open Wiki Index Page
    r = browser.open(WIKI_HOME_URL)
    parser = WikiPagesParser()
    data = r.read()
    parser.feed(data)
    pages_n = 0
    pages_to_index = []
    for suburl, title in parser.wiki_pages:
        page_name = urllib2.unquote(suburl).split('/')[-1] + WIKI_EXT + FRESH_EXT
        edit_page_url = suburl + '/edit'
        # print edit_page_url
        r = browser.open(REDMINE_URL + edit_page_url)
        wiki_edit = browser.open(REDMINE_URL + suburl + WIKI_EXT).read()
        open(page_name, 'w').write(wiki_edit)

        # --- save info about file in fileinfo.txt-new
        md5 = hashlib.md5()
        md5.update(wiki_edit)

        st = os.stat(page_name)
        pages_n += 1
        pages_to_index.append(page_name)
    print(f'Finished reading wiki index, found {pages_n} pages')
    assert len(pages_to_index) > 1, "Problem: Redmine should have at least one Wiki page"
    reindex(pages_to_index, [], METAFILE + FRESH_EXT)


def read_meta(f):
    """ read meta """
    info = []
    inp = open(f, 'r')
    RFileInfo = namedtuple('RFileInfo', ['mtime', 'md5', 'fname'])
    for line in inp.xreadlines():
        info.append(RFileInfo(*line.strip().split(' ')))
    return info


def read_choice(prompt, choices):
    """ read choice """
    while True:
        print(prompt)
        inp = raw_input('> ')
        if inp in choices:
            return inp


def upload_local_version(browser, localname):
    """ upload local version """
    print("keep_and_upload_local_version")
    # read & parse form params
    edit_page_url = WIKI_URL + localname.replace(WIKI_EXT, '')
    edit_page_form = edit_page_url + '/edit'
    r = browser.open(edit_page_form)
    wiki_edit = WikiEditPageParser()
    wiki_edit.feed(r.read().decode('utf-8'))

    # post changed data
    data = {}
    data['authenticity_token'] = wiki_edit.authenticity_token
    data['content[version]'] = wiki_edit.content_version
    data['content[text]'] = open(localname, 'r').read()
    params = urllib.urlencode(data)
    request = urllib2.Request(edit_page_url, data=params)
    request.get_method = lambda: 'PUT'
    try:
        r = browser.open(request)
    except urllib2.HTTPError:
        pass


def compare_files():
    """ compare files """
    print('Comparing...')
    remotefiles_info = read_meta(METAFILE + FRESH_EXT)
    localfiles_saved = None
    if os.path.exists(METAFILE):
        localfiles_saved = read_meta(METAFILE)
    compared = {}
    for rmtinf in remotefiles_info:
        lfile = localfname(rmtinf.fname)
        if os.path.exists(lfile):
            text = open(lfile, 'r').read()
            md5 = hashlib.md5()
            md5.update(text)

            compared[lfile] = FileStates.UNCHANGED
            if localfiles_saved:
                for locinf in localfiles_saved:
                    if locinf.fname == localfname(rmtinf.fname):
                        if rmtinf.md5 != locinf.md5:
                            if md5.hexdigest() == locinf.md5:
                                compared[lfile] = FileStates.CHANGED_REMOTE
                            else:
                                compared[lfile] = FileStates.CHANGED_BOTH

                        elif locinf.md5 != md5.hexdigest():
                            compared[lfile] = FileStates.CHANGED_LOCAL
        else:
            compared[lfile] = FileStates.LOCALLY_DELETED

    if localfiles_saved:
        for locinf in localfiles_saved:
            found = False
            for rmtinf in remotefiles_info:
                if locinf.fname == localfname(rmtinf.fname):
                    found = True
            if not found:
                compared[locinf.fname] = FileStates.REMOTELY_DELETED

    return compared


class FileStates:
    """ FileStates """
    UNCHANGED = 0
    CHANGED_BOTH = 1
    CHANGED_LOCAL = 2
    CHANGED_REMOTE = 3
    LOCALLY_DELETED = 4
    REMOTELY_DELETED = 5


def process_changes(browser, compared):
    """ process changes """
    omit_files = []
    for f in compared:
        if compared[f] == FileStates.REMOTELY_DELETED:
            print(f"D {f}")
            if os.path.exists(f):
                os.unlink(f)

        elif compared[f] == FileStates.CHANGED_BOTH or \
                compared[f] == FileStates.CHANGED_LOCAL:
            if compared[f] == FileStates.CHANGED_BOTH:
                extmsg = "both local and remote"
            else:
                extmsg = "locally"
            while True:
                c = read_choice(
                    '\nFile "{0}" is modified {1} your choice:\n'
                    '[l] keep local version\n'
                    '[s] keep server version\n'
                    '[d] run diff\n'
                    '[n] do nothing'.format(f, extmsg), ['l', 's', 'd', 'n'])

                if c == 'l':
                    upload_local_version(browser, f)
                    break
                elif c == 's':
                    os.rename(f + FRESH_EXT, f)
                    print(f'Successfully replaced {f} <- {f + FRESH_EXT}')
                    break
                elif c == 'd':
                    subprocess.call(f"diff {f + FRESH_EXT} {f}", shell=True)
                elif c == 'n':
                    omit_files.append(f)
                    break

        elif compared[f] == FileStates.LOCALLY_DELETED or \
                compared[f] == FileStates.CHANGED_REMOTE:
            print(f"U {f}")
            os.rename(f + FRESH_EXT, f)

        elif compared[f] == FileStates.REMOTELY_DELETED:
            print(f"D {f}")
            os.unlink(f)
    reindex(compared.keys(), omit_files, METAFILE)


def localfname(name):
    """ local file name """
    return name.replace(FRESH_EXT, '')


def reindex(filelist, omit_files, filename=METAFILE):
    """ reindex """
    if os.path.exists(filename):
        oldmeta = read_meta(filename)
    else:
        oldmeta = []

    with open(filename, 'w') as indexinfo:
        for fname in filelist:
            if fname in omit_files:
                continue
            if not os.path.exists(fname):
                continue

            md5 = hashlib.md5()
            md5.update(open(fname, "r").read())

            st = os.stat(fname)
            indexinfo.write(f"{st.st_mtime:.2f} {md5.hexdigest()} {fname}\n")

        for entry in oldmeta:
            if entry.fname in omit_files:
                indexinfo.write(f"{entry.mtime} {entry.md5} {entry.fname}\n")


def remove_temp_files():
    """ remove temp files """
    if os.path.exists(METAFILE + FRESH_EXT):
        remotefiles_info = read_meta(METAFILE + FRESH_EXT)
        for f in remotefiles_info:
            if os.path.exists(f.fname):
                os.unlink(f.fname)


class Command(BaseCommand):
    """ Command """
    help = ("Sync Redmine wiki pages.")

    option_list = BaseCommand.option_list

    requires_model_validation = False

    def handle(self, **options):
        main()
