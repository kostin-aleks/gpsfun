import twill
from twill import commands as cmd
from twill.namespaces import get_twill_glocals
from twill.errors import TwillAssertionError
import urllib
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
#from cStringIO import StringIO
#import unittest
import re
#import _mechanize_dist as mechanize
from django.conf import settings


TEST_TEACHER_LOGIN = 'test_teacher'
TEST_TEACHER_PASSWD = 'test'
TEST_STUDENT_LOGIN = 'test_student'
TEST_STUDENT_PASSWD = 'test'
TEST_STUDENTSET = 'test_studentset'
_last_admin_login = None

test_dir = os.path.dirname(os.path.abspath(__file__))
SITE_ROOT = os.path.normpath(os.path.join(test_dir, '../..'))

BIG_DATE = datetime(2020, 1, 1, 1, 1)




#def set_debugging(on=True):
    #""" set global debugging """

    #if on:
        #twill.set_output(None)
    #else:
        #twill.set_output(StringIO())




# used in django admin for datetime values
def admin_date(dt):
    return dt.strftime("%Y-%m-%d")

def admin_time(dt):
    return dt.strftime("%H:%M:%S")


def current_second():
    """ return unique number for current second """
    return datetime.now().strftime('%Y%M%d%H%M%S')

def uniq():
    return current_second()


def ff():
    """ show current page in firefox """

    # if not os.environ.get('DEBUG_TEST', False):
    #     return

    # turn on debugging to show
    # set_debugging(True)

    filename = '/tmp/_yp_test_%s' % uniq()  # os.tmpnam() make warnings

    f = open(filename, 'w')
    html = cmd.show()

    # replace home urls to htdocs dir urls
    html = html.replace('"/', '"%s/htdocs/' % SITE_ROOT)

    html = html.replace('url(/', 'url(%s/htdocs/' % SITE_ROOT)

    # delete rX for css version
    for r in range(7, 50):
        html = html.replace('/r%s/' % r, '/')

    f.write(html)
    f.close()
    os.system('/usr/bin/env firefox %s' % filename)


SITE = os.environ.get('YP_HOSTNAME')


def setUp(debug=False):
    cmd.clear_cookies()
    #cmd.go(SITE)
    #if not debug:
        #set_debugging(os.environ.get('DEBUG_TEST', False))
    #cmd.config('readonly_controls_writeable', '+')





def safe_browser(f):
    """ decorator: call function with independent twill browser """

    def tmp(*args, **kwargs):
        try:
            old_browser = cmd.browser
            cmd.browser = cmd.TwillBrowser()
            setUp()
            return f(*args, **kwargs)
        finally:
            cmd.browser = old_browser

    return tmp


def admin_browser(f):
    """ decorator: call function in 'admin browser' """
    def tmp(*args, **kwargs):
        try:
            old_browser = cmd.browser
            cmd.browser = _admin_browser
            #? no! setUp()
            return f(*args, **kwargs)
        finally:
            cmd.browser = old_browser

    return tmp


def safe_url(f):
    """ decorator: call function with current url restoring """

    def tmp(*args, **kwargs):
        try:
            old_url = cmd.get_browser().get_url()
            return f(*args, **kwargs)
        finally:
            cmd.go(old_url)

    return tmp


def get(url):
    cmd.go(url)
    try:
        cmd.code(200)
    except TwillAssertionError as s:
        ff()
        raise TwillAssertionError('%s url %s' % (s, fullurl(url)))


def post(url, data):
    """ POST data to url (using twill) """
    b = cmd.get_browser()
    mb = b._browser
    r = mb.open(url, urllib.urlencode(data))
    return r


#def post2(url, data):
    #""" POST data to url - just like cmd.submit() with data-form

        #data - sequence of two-element tuples or dictionary.
               #Every data value converted using str().
               #(for example, None will be converted to 'None')

        #Better use this function instead of post()
    #"""
    #b = cmd.get_browser()

    ## make full url
    #if 'http://' not in url:
        #url = cmd.url('http://[^/]*') + url

    #request = mechanize.Request(url=url, data=urllib.urlencode(data))
    #b._journey('open', request)

def post3(url, **post_kwargs):
    post2(url, data=post_kwargs)

def follow_anchor_by_name(text):
    """ sometimes follow not works somewhy. This is simplified equivalent """
    href = soup().find('a', text=text).parent['href']
    cmd.go(href)

def _soup(html):
    return BeautifulSoup(html)


def soup(cp='cp1251'):
    """ return soup based on current twill html """
    return _soup(unicode(cmd.show(), cp).encode('utf8'))


def get_local(name, default=None):
    """ return twill Local's variable value """

    g, l = get_twill_glocals()
    return l.get(name, default)


# def extract_href(tag):
#     """ extract and return href of soup tag """
#
#     if tag.has_key('onclick'):
#         onclick_value = tag.get('onclick')
#         tag_href = re.compile('href="(?P<href>.+)"').search(onclick_value).groups(0)[0]
#     else:
#         tag_href = tag.find('a').get('href')


def find_re(reg, tag=None):
    """ find re inside tag and return list of re-groups

        if tag=None then search through all html.
    """

    tag = tag or soup()

    # r = re.compile('Login: (?P<login>[\w]+)')
    # login_text = soup().find(text=r)
    # login = r.search(login_text).groupdict()['login']

    r = re.compile(reg)
    text = tag.find(text=r)
    return r.search(text).groups()


def find_cross_td(table_id, row_text, col_text):
    """ return td soup tag on crossroad of table col_text and row_text """

    table = soup().find('table', id=table_id)

    column_index = [i
                    for i, th in enumerate(table.findAll('th'))
                    if th.string == col_text][0]

    row = [tr for tr in table.findAll('tr')if tr.fetchText(row_text)][0]

    cell = row.findAll('td', limit=column_index+1)[-1]

    return cell



@safe_url
def create_student(ssid, forename, surname):
    """ create student in studentset and return id """

    post('/py/teacher/studentset/%s/' % ssid,
         dict(action='stud_add',
              namelist='%s %s' % (surname, forename),
              setID=str(ssid),
              submit='Submit',
              nameorder='dir',
              ))

    # verify student created and return info
    s = find_student_by_name(ssid, forename, surname)
    assert s, 'created student not found'

    return s


@safe_url
def find_student_by_name(ssid, forename, surname):
    """ Find student in studentset by his name. Return student id or None
    if student not found """

    cmd.go('/py/teacher/studentset/%d/' % ssid)

    tag = soup().find('input',
                      {'name': 'stud_group[]',
                       'title': '%s %s' % (forename, surname.capitalize())})

    if tag:
        return tag['value']
    else:
        return None


def admin_find_teacher(extended=False, **kwargs):
    """ find first teacher by kwargs return object dict """
    r = _admin_grid_find('/YP-admin/teachers/list/', **kwargs)

    if r and extended:
        r.update(admin_teacher_info(r['id']))

    return r


def admin_student_assignments_count(student_id):
    """ return count of assignments for student """

    return _django_admin_filter_count(\
        '/YP-admin/admin/Assignment/assignmentstudent/', student_id)


# def admin_aset_count(teacher_id):
#     """ return count of aset with given teacher """
#
#     return _django_admin_filter_count(\
#         '/YP-admin/admin/Assignment/assignmentset/', teacher_id)



def admin_find_student(extended=False, **kwargs):
    r = _admin_grid_find('/YP-admin/students/list/', **kwargs)

    if r and extended:
        r.update(admin_student_info(r['id']))

    return r


def admin_find_aset(extended=False, **kwargs):
    r = _admin_grid_find('/YP-admin/content/aset/', **kwargs)

    if r and extended:
        r.update(admin_aset_info(r['id']))

    return r


def admin_find_agroup(**kwargs):
    r = _admin_grid_find('/YP-admin/content/agroups/', **kwargs)
    if r:
        # transform teacher url to id
        r['teacher_id'] = re.match('.+/teacher/(?P<teacher_id>\d+)/',
                                   r['teacher']).groupdict()['teacher_id']

    return r


def admin_find_course(**kwargs):
    r = _admin_grid_find('/YP-admin/content/courses/', **kwargs)

    if r:
        # transform agroup url to id
        r['agroup_id'] = re.match('.+/agroup/(?P<agroup_id>\d+)/',
                                  r['agroup']).groupdict()['agroup_id']

        # transform teacher url to id
        r['teacher_id'] = re.match('.+/teacher/(?P<teacher_id>\d+)/',
                                   r['created by']).groupdict()['teacher_id']

    return r


def admin_find_studentset(extended=False, **kwargs):
    r = _admin_grid_find('/YP-admin/students/studentset', **kwargs)

    # some strange code
    # if r:
    #     # transform owner teacher url to id
    #     r['owner_id'] = re.match('.+/teacher/(?P<owner_id>\d+)/',
    #                               r['owner']).groupdict()['owner_id']

    if r and extended:
        r.update(admin_studentset_info(r['id']))

    return r


def admin_find_task(**kwargs):
    r = _admin_grid_find('/YP-admin/content/task/', **kwargs)

    if r:
        # transform course url to id
        r['course_id'] = re.match('.+/course/(?P<course_id>\d+)/',
                                  r['course']).groupdict()['course_id']

    return r


def admin_find_task_result(**kwargs):
    r = _admin_grid_find('/YP-admin/content/task_result/', **kwargs)

    if r:
        r['assignment_student_id'] = re.match(
            '.+/assignmentstudent/(?P<id>\d+)/',
            r['assignment student']).groupdict()['id']

    return r


def admin_find_task_result_page_comment(**kwargs):
    r = _admin_grid_find('/YP-admin/content/task_result_page_comment/',
                         **kwargs)

    if r:
        pass
        # todo

    return r


def admin_find_inbox_message(**kwargs):
    r = _admin_grid_find('/YP-admin/content/inbox_message/',
                         **kwargs)

    if r:
        pass
        # todo

    return r


def admin_teacher_info(id):
    """ return dictionary with teacher info of edit form """

    r = _get_django_admin_edit_info('/YP-admin/admin/Teacher/teacher/%s/' % id)

    return r


def admin_student_info(id):
    """ return dictionary with student info of edit form """

    r = _get_django_admin_edit_info('/YP-admin/admin/Student/student/%s/' % id)

    return r


def admin_aset_info(id):
    """ return dictionary with aset info of edit form """

    r = _get_django_admin_edit_info('YP-admin/admin/Assignment/assignmentset/%s/' % id)

    return r


def admin_studentset_info(ss_id):
    """ return dictionary with studentset info of edit form

        studentset students included as: {... 'students': [id, id...] ...}

    """

    r = _get_django_admin_edit_info('/YP-admin/admin/StudentSet/studentset/%s/' % ss_id)

    return r

@admin_browser
def admin_create_teacher(**kwargs):
    """ create teacher in admin with given properties and return id """
    passwd = kwargs['passwd']
    del kwargs['passwd']
    teacher_id = _django_admin_change_object('/YP-admin/admin/Teacher/teacher/add/', **kwargs)
    cmd.go('/YP-admin/admin/Teacher/teacher/%s/password/' % teacher_id)
    cmd.showforms()
    cmd.fv(1, 'password', passwd)
    cmd.fv(1, 'retype_password', passwd)
    cmd.submit()
    return teacher_id


def admin_create_agroup(**kwargs):
    """ create agroup in admin with given properties and return id  """
    return _django_admin_change_object('/YP-admin/admin/Agroup/agroup/add/', **kwargs)


def admin_create_course(**kwargs):
    """ create course in admin with given properties and return id """
    return _django_admin_change_object('/YP-admin/admin/Course/course/add/', **kwargs)




@admin_browser
def admin_create_studentset(**kwargs):
    """ create studentset in admin with given properties and return id """

    # big default date expire
    kwargs['date_expire_0'] = kwargs.get('date_expire_0', admin_date(BIG_DATE))
    kwargs['date_expire_1'] = kwargs.get('date_expire_1', '00:00:00')

    # default teacher
    if kwargs.has_key('studentsetteachermember_set-0-teacher'):

        kwargs['studentsetteachermember_set-0-member_since_0'] = \
            kwargs.get('studentsetteachermember_set-0-member_since_0',
                       admin_date(datetime.now()))
        kwargs['studentsetteachermember_set-0-member_since_1'] = \
            kwargs.get('studentsetteachermember_set-0-member_since_1',
                       '00:00:00')

        kwargs['studentsetteachermember_set-0-status'] = \
            kwargs.get('studentsetteachermember_set-0-status', 'member')

    return _django_admin_change_object('/YP-admin/admin/StudentSet/studentset/add/', **kwargs)



def admin_create_student(**kwargs):
    """ create student in admin with given properties and return id  """

    return _django_admin_change_object('/YP-admin/admin/Student/student/add/', **kwargs)


def admin_create_aset(**kwargs):
    """ create aset in admin with given properties and return id  """

    return _django_admin_change_object('/YP-admin/admin/Assignment/assignmentset/add/', **kwargs)


# hard to realize - need through_id... so use create_task instead
# def admin_create_task(**kwargs):
#     """ create task (new) in admin with given properties and return id """
#     return _django_admin_change_object('/YP-admin/admin/Task/task/add/', **kwargs)


@admin_browser
def _django_admin_change_object(url, **kwargs):
    """ create/edit object in django admin and return his id

    url - url of django object modify form
    kwargs - form fields and values

    """
    cmd.go(url)
    cmd.find('Save and continue editing')
    for k, v in kwargs.iteritems():
        # send checked checkboxes as 'on', unchecked not send.
        if type(v) == bool:
            if v:
                cmd.fv(1, k, 'on')
            else:
                pass
        else:
            # default
            cmd.fv(1, k, str(v))

    cmd.submit('_continue')

    try:
        cmd.notfind('Please correct the error below')
    except TwillAssertionError as e:
        print('Page errors: %s' % soup().findAll('ul', {'class': 'errorlist'}))
        ff()
        raise

    try:
        cmd.find('was \w* successfully. You may edit it again below.')
    except TwillAssertionError as e:
        ff()
        raise

    id = cmd.url('.*/(?P<id>\d+)/')

    return id



@admin_browser
def _admin_grid_find(grid_url, restore_config='full_default', **kwargs):
    """ find in alex admin grid first row with kwargs props

     Return dictionary with found object names and values:
      - names are took from grid column names
      - values are took from first grid data row.
        Note: for link cells the link url is used.

    Params:
      grid_url - relative url of grid with all objects
      restore_config - config for grid. By default used not existing (=default)
      **kwargs - properties and values search by


    """
    admin_login()

    url_params = {'action': 'start_search', 'table': 'admintable'}

    for k, v in kwargs.iteritems():

        # modify some keys and values
        if k == 'id': # id is always integer
            url_key = '%s:integer AUTO_INCREMENT:eq' % k
            url_params[url_key] = v
        elif v == None:  #  None value
            url_key = '%s:varchar(4):null' % k
            url_params[url_key] = 'true'
        else: # default
            url_key = '%s:varchar(32):eq' % k
            url_params[url_key] = v

    # restore full default config
    config_name = _last_admin_login + '-' + restore_config
    url_params.update({'restore': config_name})

    grid_url = '%s?%s' % (grid_url, urllib.urlencode(url_params))

    cmd.go(grid_url)
    cmd.find(' List')

    admin_table_html = soup().find('table', {'class': 'admintable'})
    fields_tr = admin_table_html.findAll('th')
    fields = [th.string for th in fields_tr]

    values_tr = admin_table_html.find('tr', {'class': 'odd'})

    if values_tr:

        # extract string value or href for
        values = [td.string or td.find('a') and td.find('a').get('href')
                  for td in values_tr.findAll('td')]

        result = dict(zip(fields, values))

        # exclude technical columns
        for k in [' ', 'action']:
            result.pop(k, None)

        # hack: replace key 'ID'  to 'id'
        # (because django set verbose_name='ID' to auto-id fields)
        if 'ID' in result: # (speed): and not result.has_key('id')
            result['id'] = result.pop('ID', None)

    else:
        result = None

    return result


@admin_browser
def _get_django_admin_edit_info(edit_url):
    """ Return dictionary of all text inputs found  on page by edit_url:
      {<name>: <value>,
       ...
       <inline group>s: [id, id...]
       ...
      }

    """
    admin_login()
    cmd.go(edit_url)

    r = {}
    # gather info from simple text inputs
    r.update([(inp['name'], inp.get('value'))
              for inp in soup().findAll('input',
                                        {'class': 'vTextField'})
              if not '_set-' in inp['name']
             ]
            )

    # gather info from id inputs (including inline groups)
    fk_inputs = soup().findAll('input', {'class': 'vForeignKeyRawIdAdminField'})
    for inp in fk_inputs:
        if not inp.has_key('value'):
            continue
        name = inp['name']
        value = inp['value']

        if '_set-' in name:
            # inline group
            group_name = name.split('-')[-1] + 's' # multiple
            r[group_name] = r.get(group_name, []) + [value]
        else:
            r[name] = value

    # todo: here also can gather info from other inputs (checkboxes, etc)

    return r




def delete_agroup(id):
    post('/py/teacher/agroup/%s/delete/' % id,
         dict(agroup=id, delete='Delete'))

    # verify agroup not exists
    cmd.go('/py/teacher/agroup/list/')
    cmd.notfind('py/teacher/agroup/%s/' % id)


def admin_delete_teacher(id):
    _django_admin_delete_object(
        '/YP-admin/admin/Teacher/teacher/%s/delete/' % id)


def admin_delete_agroup(id):
    _django_admin_delete_object(
        '/YP-admin/admin/Agroup/agroup/%s/delete/' % id)


def admin_delete_course(id):
    _django_admin_delete_object(
        '/YP-admin/admin/Course/course/%s/delete/' % id)


def admin_delete_studentset(id):
    _django_admin_delete_object(
        '/YP-admin/admin/StudentSet/studentset/%s/delete/' % id)


def admin_delete_assignmentstudent(id):
    _django_admin_delete_object(
        '/YP-admin/admin/Assignment/assignmentstudent/%s/delete/' % id)


def admin_delete_assignmentset(id):
    _django_admin_delete_object(
        '/YP-admin/admin/Assignment/assignmentset/%s/delete/' % id)


def admin_delete_task_result_page_comment(id):
    _django_admin_delete_object(
        '/YP-admin/admin/Task/taskresultpagecomment/%s/delete/' % id)


def admin_delete_inbox_message(id):
    _django_admin_delete_object(
        '/YP-admin/admin/Inbox/inboxmessage/%s/delete/' % id)


def _django_admin_delete_object(url):
    """ delete object with id from django admin by url """
    admin_login()
    cmd.go(url)
    cmd.code(200)
    cmd.find('Are you sure?')
    cmd.submit()
    cmd.find('deleted successfully')


@admin_browser
def _django_admin_filter_count(url, filter):
    """ in django admin goto url and appliy filter/search and
        return found records count """

    admin_login()
    cmd.go(url)
    cmd.find('Select .* to change')
    cmd.fv(2, 'q', filter)
    cmd.submit()
    cmd.code(200)

    #<span class="small_quiet">2 results ...
    count = soup().find('span', {'class': 'small quiet'}).contents[0].split()[0]

    return int(count)


def get_test_teacher():
    """ return test teacher dict. create if not exitst. """

    t = admin_find_teacher(login=TEST_TEACHER_LOGIN)

    if not t:
        id = admin_create_teacher(forename='test',
                                  surname='test',
                                  login=TEST_TEACHER_LOGIN,
                                  passwd=TEST_TEACHER_PASSWD,
                                  email=settings.TEST_TEACHER_EMAIL)

        t = admin_find_teacher(id=id)

    t['passwd'] = TEST_TEACHER_PASSWD   # little hack

    return t


TEST_AGROUP_NAME = 'test_agroup'

def get_test_agroup():
    """ return test agroup dict. create if not exitst. """

    teacher = get_test_teacher()
    ag = admin_find_agroup(name=TEST_AGROUP_NAME, teacher=teacher['id'])
    if not ag:
        agroup_id = create_agroup(name='test_agroup',
                                  description='desc'*25,
                                  permissions='',  # private
                                  unit=0,           # unknown
                                  )
        # use this when fixed: http://bugz.halogen-dg.com/show_bug.cgi?id=14284
        # id = admin_create_agroup(name='test_agroup',
        #                          description='desc'*25,
        #                          perm='',
        #                          teacher=teacher['id'],
        #                          unit=0, #unknown
        #                          )

        ag = admin_find_agroup(id=agroup_id)

    return ag


def get_test_course():
    """ return test course dict. create if not exitst. """

    teacher = get_test_teacher()
    agroup = get_test_agroup()
    course = admin_find_course(agroup=agroup['id'], name='test_course')

    if not course:
        course_id = admin_create_course(agroup=agroup['id'],
                                        created_by=teacher['id'],
                                        name='test_course',
                                        access='private',
                                        )

        course = admin_find_course(id=course_id)

    return course


def get_test_task():
    """ return test task as dict. create if not exitst. """

    teacher = get_test_teacher()
    course = get_test_course()

    task = admin_find_task(course=course['id'], name='test_task')

    if not task:
        through_id = create_task(course['id'],
                                 'test_task',
                                 'my instructions',
                                 )

        task = admin_find_task(through_id=through_id)

    return task


def get_test_task_result():
    """ return test task as dict """

    task = get_test_task()

    # assume test task result is first task_result for task...
    task_result = admin_find_task_result(task=task['id'])

    return task_result


def teacher_login(username='alex2', password='pong'):
    cmd.go('/py/teacher/login/')

    cmd.fv(1, 'login', username)
    cmd.fv(1, 'password', password)

    cmd.submit()
    #alt: post('/py/teacher/login/', data=dict(login='alex2', password='pong'))

    cmd.code(200)
    cmd.go('/py/teacher/')

    cmd.notfind('type="password"')


def teacher_logout():
    cmd.go('/py/teacher/logout/')


def test_teacher_login():
    """ login using test teacher """

    teacher = get_test_teacher()
    teacher_login(teacher['login'], teacher['passwd'])


def test_student_login():
    """ login using test student """

    student = get_test_student()
    student_login(student['login'], student['passwd'])


@safe_browser
def get_teacher_capture():
    """ return capture for last request """

    admin_login()

    cmd.go('/YP-admin/admin/Request/request/')
    last_request_link = soup().find('tr', {'class': 'row1'}).find('a')['href']

    cmd.go(last_request_link)
    capture = soup().find('input', id='id_verifykey')['value']

    return capture


@safe_url
def create_studentset(studentset_name, students='', access_type='formal'):
    """ add studentset and return info """
    assert access_type in ['formal', 'casual']
    cmd.add_extra_header('Content-Type', 'application/xml')
    cmd.add_extra_header('charset', 'UTF-8')
    b = cmd.get_browser()
    mb = b._browser

    r = mb.open('/py/teacher/studentset/new/ajax/?',
                urllib.urlencode(dict(setname=studentset_name,
                                      namelist=students,
                                      access_type=access_type,
                                      nameorder='dir',
                                      submit='Submit')))
    cmd.go('/py/teacher/studentset/list/')

    id = int(soup().findAll(text=studentset_name)[0].parent['href'].split('/')[-2])

    return get_studentset_info(id)


def create_agroup(**kwargs):
    """ create agroup and return id """

    name = kwargs.get('name')

    r = post('/py/teacher/agroup/list/',
             dict(agroup_name=name,
                  description=kwargs.get('description'),
                  #colophon=   todo
                  permissions=kwargs.get('permissions'), # private
                  submit='Submit'))

    soup = _soup(r.get_data())

    errors = soup.findAll('ul', {'class': 'errorlist'})
    if errors:
        raise AssertionError('Error agroup creation: %s' % errors)
    else:
        r = re.compile('py/teacher/agroup/(?P<agroup_id>\d+)/')
        agroup_a = soup.find('a', href=r, text=name).parent
        id = r.search(agroup_a['href']).groupdict()['agroup_id']

    return id


def create_course(agroup_id, **kwargs):
    """ create course (with kwarg parameters) in agroup and return id """

    if 'gradegridset' not in kwargs:
        kwargs['gradegridset']=1

    post2('/py/teacher/agroup/%s/course_list/' % agroup_id,
          dict(action='addcourse',
               course_name=kwargs['name'],
               gradegridset=kwargs['gradegridset'],
               description=kwargs.get('description'),
               submit='Submit'))


    errors = soup().findAll('ul', {'class': 'errorlist'})
    if errors:
        raise AssertionError('Page errors: %s' % errors)
    else:
        id = cmd.url('.*/course/(?P<course_id>\d+)/edit/')

    return id


def create_task(course_id, name, instructions, template='epf', **kwargs):
    """ create task and return through_id

       kwargs - additional parameters

    """
    agroup_id = admin_find_course(id=course_id)['agroup_id']

    cmd.go('/py/teacher/agroup/%s/course/%s/task/new/' % (agroup_id, course_id))

    cmd.fv(1, 'task_name', name)
    cmd.fv(1, 'task_template', template)
    cmd.submit()

    through_id = cmd.url('.+/task/(?P<task_through_id>\d+)/edit/')

    cmd.fv(1, 'instructions', instructions)
    cmd.submit('save')

    errors = soup().findAll('ul', {'class': 'errorlist'})
    if errors:
        raise AssertionError('Page errors: %s' % errors)

    cmd.find('Changes saved')

    return through_id


def delete_task(through_id):
    task = admin_find_task(through_id=through_id)
    course_id = task['course_id']
    agroup_id = admin_find_course(id=course_id)['agroup_id']

    cmd.go('/py/teacher/agroup/%s/course/%s/task/%s/remove/'\
           % (agroup_id, course_id, through_id))

    cmd.submit()

    cmd.find('was removed successfully')


def delete_course(id):
    course = admin_find_course(id=id)

    post2('/py/teacher/agroup/%s/course/%s/delete/' % (course['agroup_id'], id),
          dict(course=id, delete='Delete'))

    cmd.url('.*/course_list/')

    cmd.notfind('course/%s' % id) # in href


def agroup_join(agroup_id):

    cmd.go('/py/teacher/agroup/%s/join/' % str(agroup_id))

    #cmd.find('Sign up - step 1/2')
    cmd.fv('YPform', 'message', "test teacher want join to this group " * 3)
    cmd.submit()

    cmd.go('/py/teacher/agroup/%s/' % str(agroup_id))


def agroup_leave(agroup_id):
    cmd.go('/py/teacher/agroup/%s/leave/' % str(agroup_id))

    cmd.submit()

    cmd.go('/py/teacher/agroup/%s/' % str(agroup_id))


@safe_url
def find_studenset(name):
    """ find studenset by name and return info. If not found return None """

    cmd.go('/py/teacher/studentset/list/')

    found_text = soup().find('a', text=name)

    if found_text:
        id = found_text.parent['href'].split('/')[-2]
        return get_studentset_info(id)
    else:
        return None


@safe_url
def get_studentset_info(id):
    """ get existing studentset info """

    # key
    cmd.go('/py/teacher/studentset/list/')

    key = soup().find('a', href='/py/teacher/studentset/%s/key/reset/' % id)\
          .parent.previousSibling.previousSibling.string.strip()

    return {'id': id,
            'key': key,
            #'access_type':
            }


def studentset_leave(id, teacher_id=221):
    cmd.go('/py/teacher/studentset/%d/' % id)
    cmd.code(200)
    b = cmd.get_browser()
    mb = b._browser
    r = mb.open('/py/teacher/studentset/teacher_remove/',
                urllib.urlencode({'setID': id,
                                  'remove': 'Remove',
                                  'id_list[]': '221'}))


def remove_students(ssid, students_list):
    b = cmd.get_browser()
    mb = b._browser
    params = [
        ('setID', ssid),
        ('remove', 'Remove'),
        ('id_list[]', ','.join([str(d) for d in students_list]))]
    r = mb.open('/py/teacher/studentset/student_remove/',
                urllib.urlencode(params))


def assign(ssid, content):
    cmd.go('/py/teacher/assignment/new/')
    cmd.find(content[0])
    soup = BeautifulSoup(cmd.show())
    cmd.go(soup.find('a', text=content[0]).parent['href'])
    soup = BeautifulSoup(cmd.show())
    cmd.go(soup.find('a', text=content[1]).parent['href'])
    soup = BeautifulSoup(cmd.show())
    assignment = soup.find('b', text=content[2]).parent.parent.parent.find('input')['value']
    cmd.fv(2, 'task', assignment)
    cmd.config('readonly_controls_writeable', '+')
    cmd.fv(2, 'mainform_force_next', 'yes')
    cmd.submit()
    b = cmd.get_browser()
    mb = b._browser
    r=mb.open(b.get_url(), 'studentset_id=%d' % ssid)
    cmd.submit()


def leave_all_studentsets_named(studentset_name):
    b = cmd.get_browser()
    cmd.go("/py/teacher/studentset/list/")
    soup=BeautifulSoup(cmd.show())
    for tststudentset in soup.findAll('a', text=studentset_name):
        stsid = int(tststudentset.parent['href'].split('/')[-2])
        studentset_leave(stsid)


def get_studentset_students(ssid):
    """ return list of student id belonged to studentset ssid """
    # if studentset_name:
    #     go('/py/teacher/studentset/list/')
    #     soup=BeautifulSoup(show())
    #     go(soup.find('a',text='formal-class').parent['href'])
    # else:
    cmd.go('/py/teacher/studentset/%s/' % ssid)

    return [int(d['value'])
            for d in soup().findAll('input', {'name': "stud_group[]"})]


@safe_url
def get_student_info(student_id, ssid):
    cmd.go('/py/teacher/studentset/student/%s/edit/studentset/%s/' \
         %(student_id, ssid))
    soup=BeautifulSoup(cmd.show())
    return dict(id=student_id,
                ssid=ssid,
                login=soup.find('td',
                                {'class': 'first-cell'},
                                text='Login').parent.parent.find('td',
                                                                 {'class':
                                                                  'second-cell'}).string,
                password=soup.find('input', {'id': 'id_passwd'})['value'],
                forename=soup.find('input', {'id': 'id_forename'})['value'],
                surname=soup.find('input', {'id': 'id_surname'})['value'])


def student_login(login, password):
    """ login student by username and password """
    cmd.go('/py/student/login/')
    cmd.fv(1, 'login', login)
    cmd.fv(1, 'passwd', password)
    cmd.submit()
    cmd.find('Attempts/Cards')


def student_logout():
    """ logout student """
    cmd.go('/py/student/logout/')
    cmd.url('/py/student/login')


def set_cookie(domain, name, value, expires=(datetime.now()+timedelta(days=365)).strftime("%Y-%m-%d %H:%M:%S")):
    """ idea from http://www.mail-archive.com/twill@lists.idyll.org/msg00951.html """
    cookie_file = "cookies.txt"

    params = dict(domain=domain,
                  name=name,
                  value=value,
                  expires=expires)

    cmd.save_cookies(cookie_file)
    cookie = open(cookie_file, "a+")
    cookie.write('Set-Cookie3: %(name)s=%(value)s; '\
                 'path="/"; domain="%(domain)s"; path_spec; domain_dot; '\
                 'expires="%(expires)s"; version=0' % params)
    cookie.flush()
    cmd.load_cookies(cookie_file)
    os.unlink(cookie_file)



def admin_login(username='alex', password='zec6Zai2'):
    # admin session
    is_admin_session = 'admin_session' in [c.name for c in cmd.browser.cj]

    # search amin session in
    global _last_admin_login
    if _last_admin_login != username or not is_admin_session:
        cmd.go('/YP-admin/login/?next=/YP-admin/')
        cmd.fv(1, 'username', username)
        cmd.fv(1, 'password', password)
        cmd.submit()
        cmd.notfind("Your username and password didn't match")
        _last_admin_login = username


def fullurl(url):
    return os.environ.get('YP_HOSTNAME') + url



def create_teacher(forename, surname, institution, email, country, title=''):
    """ create teacher and return {id, login} info dict """
    cmd.go('/py/teacher/login/')
    cmd.find('logging into Yacapaca')

    cmd.follow('here') # for signup click here

    cmd.find('Sign up - step 1/2')
    cmd.fv(2, 'forename', forename)
    cmd.fv(2, 'surname', surname)
    cmd.fv(2, 'institution', institution)
    cmd.fv(2, 'agree', 'on')
    cmd.submit()

    cmd.find('Sign up - step 2/2')
    cmd.fv(2, 'title', title)
    cmd.fv(2, 'email', email)
    cmd.fv(2, 'country', country)
    capture = get_teacher_capture()
    cmd.fv(2, 'confirm', capture)
    cmd.submit()

    cmd.find('Registration has been completed')

    r = re.compile('Login: (?P<login>[\w]+)')
    login_text = soup().find(text=r)
    login = r.search(login_text).groupdict()['login']

    admin_login()
    teacher_list_url = '/YP-admin/teachers/list/?' + \
                       urllib.urlencode({'action': 'start_search',
                                         'table': 'admintable',
                                         'login:varchar(32):eq': login})

    cmd.go(teacher_list_url)
    cmd.find('Teachers List')
    id = soup().find('td', {'class': 'selchk'}).nextSibling.nextSibling.string

    return dict(login=login, id=id)


def delete_teacher(id):
    admin_login()

    cmd.go('/YP-admin/teachers/%s/delete/' % id)
    cmd.find('Delete teacher')

    cmd.submit()

    cmd.find('deleted successfully')




@admin_browser
def get_test_studentset():
    """ return test studentset dict.

        create if not exists (with test student and assign to test_teacher)
    """

    r = admin_find_studentset(extended=True, name=TEST_STUDENTSET)

    if not r:
        test_teacher = get_test_teacher()
        big_date = datetime.now() + timedelta(days=365*10)
        small_date = datetime.now().strftime("%Y-%m-%d")
        id = admin_create_studentset(**{
            'name': TEST_STUDENTSET,
            'access_key': 'TAKE',
            'owner': test_teacher['id'],
            'studentsetstudent_set-0-student': get_test_student()['id'],
            'studentsetteachermember_set-0-teacher': test_teacher['id']
            })
        r = admin_find_studentset(id=id)

    return r


def get_test_student():
    """ return test student info dict """

    r = admin_find_student(extended=True, login=TEST_STUDENT_LOGIN)
    if not r:
        id = admin_create_student(**{
            'forename': 'Ivan',
            'surname': 'Ivanov',
            'login': TEST_STUDENT_LOGIN,
            'passwd': TEST_STUDENT_PASSWD,
            #(in ss) 'studentsetstudent_set-0-studentset': get_test_studentset()['id']
            })
        r = admin_find_student(extended=True, id=id)

    return r


def get_test_aset():
    """ return test aset info dict """

    test_ss = get_test_studentset()

    r = admin_find_aset(extended=True,
                        studentset=test_ss['id'],
                        teacher=get_test_teacher()['id'])

    if not r:
        # create aset (and assign to test_student)
        id = create_aset(get_test_task()['id'],
                         test_ss['id'],
                         [get_test_student()['id']])

        # id = admin_create_aset(**{
        #     'studentset': get_test_studentset()['id'],
        #     'teacher': get_test_teacher()['id'],
        #     'note': 'test aset',
        #     })

        r = admin_find_aset(extended=True, id=id)

    return r


def create_aset(task_id, studentset_id, student_id_list, **kwargs):
    """ assign task to several students and return assignmentset_id

       kwargs - additional parameters

    """
    task = admin_find_task(id=task_id)
    course_id = task['course_id']
    course = admin_find_course(id=course_id)
    agroup_id = course['agroup_id']

    cmd.go('/py/teacher/assignment/new/step3/myown/0/0/%s/' % course_id)

    post2('/py/teacher/assignment/new/step3/myown/0/0/%s/' % course_id,
          dict(task='task:%s' % task['id'], mainform_force_next='yes'))
    cmd.code(200)

    cmd.url('.*/step4/.*/task:%s/0/' % task['id'])

    params = [('save', 'Finish'), ('studentset_id', studentset_id)]
    params.extend([('students', id) for id in student_id_list])

    post2('/py/teacher/assignment/new/step4/myown/0/0/%s/task:%s/0/'\
          % (course_id, task['id']),
          params)
    cmd.code(200)

    cmd.find('New assignments have been added successfully')

    r = re.compile('/student/task.php/\d+/work\?teach=\d+&aset=(?P<assignmentset_id>\d+)')
    assignmentset_id_text = soup().find('a', href=r)['href']
    assignmentset_id = r.search(assignmentset_id_text).groupdict()['assignmentset_id']

    return assignmentset_id


def delete_assignmentset(id):
    cmd.go('/py/teacher/assignment/')
    found = soup().find('input', value=str(id))
    if not found:
        raise AssertionError('Assignment not found')

    post2('/py/teacher/assignment/', (('form_assign_del_sent', '1'),
                                      ('action', 'delete'),
                                      ('delete', 'Delete'),
                                      ('id_list[]', str(id)),
                                     ))

    cmd.code(200)

def student_casual_register(access_key, login):
    cmd.go('/py/student/login/')
    cmd.show()
    cmd.fv(2,'full_access_key',access_key)
    cmd.submit()

    no = re.search(re.compile('(\/py\/student\/login\/\d+-\w+\/join\/register\/)'),
                   cmd. show()).groups()[0]
    cmd.go(no)
    cmd.fv(1,'forename','generic')
    cmd.fv(1,'surname','robot')
    cmd.fv(1,'login',login)
    cmd.fv(1,'passwd','mymy')
    cmd.fv(1,'passwd2','mymy')
    cmd.submit()
    cmd.url('/py/student/')



# cmd function synonyms
go = cmd.go
find = cmd.find
#get_browser = cmd.get_browser
reset_browser = cmd.reset_browser
extend_with = cmd.extend_with
#exit = cmd.exit
go = cmd.go
#reload = cmd.reload
url = cmd.url
code = cmd.code
follow = cmd.follow
find = cmd.find
notfind = cmd.notfind
back = cmd.back
show = cmd.show
echo = cmd.echo
save_html = cmd.save_html
sleep = cmd.sleep
agent = cmd.agent
showforms = cmd.showforms
showlinks = cmd.showlinks
showhistory = cmd.showhistory
submit = cmd.submit
formvalue = cmd.formvalue
fv = cmd.fv
formaction = cmd.formaction
fa = cmd.fa
formclear = cmd.formclear
formfile = cmd.formfile
getinput = cmd.getinput
getpassword = cmd.getpassword
save_cookies = cmd.save_cookies
load_cookies = cmd.load_cookies
clear_cookies = cmd.clear_cookies
show_cookies = cmd.show_cookies
add_auth = cmd.add_auth
run = cmd.run
runfile = cmd.runfile
setglobal = cmd.setglobal
setlocal = cmd.setlocal
debug = cmd.debug
title = cmd.title
#exit = cmd.exit
config = cmd.config
tidy_ok = cmd.tidy_ok
redirect_output = cmd.redirect_output
reset_output = cmd.reset_output
redirect_error = cmd.redirect_error
reset_error = cmd.reset_error
add_extra_header = cmd.add_extra_header
show_extra_headers = cmd.show_extra_headers
clear_extra_headers = cmd.clear_extra_headers
info = cmd.info


# class Page:
#     id = None
#     url = None
#
#     # @abstractmethod
#     # def url(self):
#     #     """ return url of page """
#     #     pass
#
#     def __init__(id, *args, **kwargs):
#         super(Page, self).__init__(*kargs, **kwargs)
#
#         self.id = id
#
#         go(self.url)


class Page(object):
    @property
    def url(self):
        return cmd.browser.get_url()


class TeacherHomePage(Page):
    def __init__(self, *args, **kwargs):
        super(TeacherHomePage, self).__init__(*args, **kwargs)
        go('/py/teacher/')


    def follow_my_studentsets_page(self):
        follow('Students')
        follow('My Student Sets')
        return MyStudentsetsPage()



class MyStudentsetsPage(Page):
    """ Students -> My Student Sets """

    def follow_studentset_page(self, name):
        #follow(name) # somewhy not works
        follow_anchor_by_name(name)

        find(name)
        return StudentsetPage()


    def get_or_create_studentset(self,
                                 name,
                                 students,
                                 access_type='formal'):
        """ create studentset (if not exists) and return info dict """

        try:
            find(name)
        except TwillAssertionError:

            # below code can be simplified
            assert access_type in ['formal', 'casual']
            cmd.add_extra_header('Content-Type', 'application/xml')
            cmd.add_extra_header('charset', 'UTF-8')
            b = cmd.get_browser()
            mb = b._browser

            r = mb.open('/py/teacher/studentset/new/ajax/?',
                        urllib.urlencode(dict(setname=name,
                                              namelist=students,
                                              access_type=access_type,
                                              nameorder='dir',
                                              submit='Submit')))

            # # return info
            # cmd.go('/py/teacher/studentset/list/')
            # id = int(soup().findAll(text=name)[0].parent['href'].split('/')[-2])
            # return get_studentset_info(id)

        return dict(name=name, )




class StudentsetPage(Page):
    """ Students -> My Student Sets -> <ss> """

    @property
    def id(self):
        return url('.*/studentset/(?P<ss_id>\d+)/')


    def add_student(self, forename, surname):
        """ add student to ss and return short info"""

        title = '%s %s' % (surname, forename)

        post3(self.url,
              setID=self.id,
              action='stud_add',
              namelist=title,
              nameorder='rev',
              submit='Submit')

        find(title)

        return dict(forename=forename, surname=surname, title=title)


    def find_student(self, forename, surname):
        title = '%s %s' % (surname, forename)
        find(title)

    def notfind_student(self, forename, surname):
        title = '%s %s' % (surname, forename)
        notfind(title)


    def get_student_id(self, forename, surname):
        student_title = surname + ' ' + forename
        student_url = soup().find('a', text=student_title).parent['href']
        student_id = re.search('/student/(?P<id>\d+)/', student_url).groups()[0]

        return student_id


    def delete_student(self, forename, surname):

        student_id = self.get_student_id(forename, surname)

        post3('/py/teacher/studentset/student_remove/',
              **{'setID': self.id,
                 'action': 'remove',
                 'id_list[]': student_id}
              )

        notfind(forename + ' ' + surname)

    def move_student(self, student_id, target_ss_id):
        """ move student to other studentset """

        post3(self.url,
              **{'setID': self.id,
                 'action': 'stud_move',
                 'set_keys': target_ss_id,
                 'id_list[]': student_id}
              )

    def copy_student(self, student_id, target_ss_id):
        """ copy student to other studentset """

        post3(self.url,
              **{'setID': self.id,
                 'action': 'stud_copy',
                 'set_keys': target_ss_id,
                 'id_list[]': student_id}
              )


    def follow_my_studentsets_page(self):
        follow('My Student Sets')
        return MyStudentsetsPage()

    def get_target_studentsets(self):
        """ return studentsets that student can be moved/copied to

        return value: {'ss_name': ss_id, ...}  """

        l =  [(option.string, option['value'])
              for option in soup().find('form', dict(name='form_stud_move'))\
                                  .findAll('option', value=re.compile('\d*'))
              ]
        return dict(l)

    def get_students(self):
        """ return dict of ss students in format:
            {'surname forename': id, ...} """

        l =  [(tag['title'], tag['value'])
              for tag in soup().find('form', dict(name='ssetform'))\
                               .findAll('input', dict(type='checkbox',
                                                      name='stud_group[]'))
              ]

        return dict(l)


