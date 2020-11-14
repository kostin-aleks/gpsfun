#!/usr/bin/python

import unittest
from django.test import TestCase
from hdg.djangoapps.admintable.models import AdminTable, DataSource, GeneratedColumn
from django.contrib.auth.models import User, AnonymousUser
from django.utils.translation import ugettext_lazy as _
from django.http import QueryDict
import datetime

def add_test_user_record(unique_key):
    u=User(username='%susername' % unique_key,
           first_name='%sfirst_name' % unique_key,
           last_name='%slast_name' % unique_key,
           email = '%s@email.tst.koval.kharkov.ua' % unique_key,
           password = '%spassword' % unique_key,
           is_staff = False,
           is_active = False,
           is_superuser = False)
    u.save()
    return u

# def set_request_from_params(request, method, params):
#     for p in params:
#         getattr(request,method).setlist([p[0]],p[1])
#     return request

def add_n_test_users(n, nstart=0):
    for i in range(nstart,nstart+n):
        lastone = add_test_user_record(i)
    lastone.last_login=datetime.datetime.now()
    lastone.save()

class FakeRequest:
    def __init__(self):
        self.GET=QueryDict('').copy()
        self.POST=QueryDict('').copy()
        self.META={'PATH_INFO':''}
        self.session={}
        self.method=''
        self.user = AnonymousUser()

    def _REQUEST(self):
        r = self.GET
        r.update(self.POST)
        return r
    REQUEST = property(_REQUEST, None)

    def __str__(self):
        res = '\n--- Request ---\n'
        for t in ['GET', 'POST', 'META', 'session']:
            res += '%s:\n' % t
            for v in getattr(self,t).keys():
                res += " %s=%s\n" % (v,getattr(self,t)[v])
        res += '-----------------'
        return res

def user_columns():
    from django.db import models
    import datetime
    columns = []
    columns.append(('id', models.AutoField(_('ID'), primary_key=True)))
    columns.append(('username', models.CharField(_('username'), max_length=30, unique=True, help_text=_("Required. 30 characters or fewer. Alphanumeric characters only (letters, digits and underscores)."))))
    columns.append(('first_name', models.CharField(_('first name'), max_length=30, blank=True)))
    columns.append(('last_name', models.CharField(_('last name'), max_length=30, blank=True)))
    columns.append(('email', models.EmailField(_('e-mail address'), blank=True)))
    columns.append(('password', models.CharField(_('password'), max_length=128, help_text=_("Use '[algo]$[salt]$[hexdigest]' or use the <a href=\"password/\">change password form</a>."))))
    columns.append(('is_staff', models.BooleanField(_('staff status'), default=False, help_text=_("Designates whether the user can log into this admin site."))))
    columns.append(('is_active', models.BooleanField(_('active'), default=True, help_text=_("Designates whether this user should be treated as active. Unselect this instead of deleting accounts."))))
    columns.append(('is_superuser', models.BooleanField(_('superuser status'), default=False, help_text=_("Designates that this user has all permissions without explicitly assigning them."))))
    columns.append(('last_login', models.DateTimeField(_('last login'), default=datetime.datetime.now)))
    columns.append(('date_joined', models.DateTimeField(_('date joined'), default=datetime.datetime.now)))
    #columns.append(('groups', models.ManyToManyField('Group', verbose_name=_('groups'), blank=True, help_text=_("In addition to the permissions manually assigned, this user will also get all permissions granted to each group he/she is in."))))
    #columns.append(('user_permissions', models.ManyToManyField('Permission', verbose_name=_('user permissions'), blank=True)))
    return columns


class AdminTableTest(TestCase):


    def test_check_query_rows_and_cols(self):
        add_n_test_users(3)
        table = AdminTable(User.objects.all())

        def check_1():
            assert table.columns()==[('id', u'ID'), ('username', u'username'), ('first_name', u'first name'), ('last_name', u'last name'), ('email', u'e-mail address'), ('password', u'password'), ('is_staff', u'staff status'), ('is_active', u'active'), ('is_superuser', u'superuser status'), ('last_login', u'last login'), ('date_joined', u'date joined')], table.columns()

            assert len(list(table.rows()))==3
            assert [r[2]['data'] for r in table.rows()]==[u'0first_name', u'1first_name', u'2first_name'], [r[2] for r in table.rows()]

        check_1()

        ds = DataSource()
        ds.set_tables('auth_user')
        ds.set_columns(user_columns())

        table = AdminTable(ds)
        check_1()


    def test_generated_column(self):
        add_n_test_users(1)
        table = AdminTable(User.objects.all())
        table.rows_per_page = 2
        table.add_column(GeneratedColumn('action'))
        for r in table.rows():
            assert r[11]['data']=='--generated column action--'

    def test_count(self):
        add_n_test_users(12)
        table = AdminTable(User.objects.all())

        ds = DataSource()
        ds.set_tables('auth_user')
        ds.set_columns(user_columns())
        table2 = AdminTable(ds)

        assert table.count() == table2.count(), "%d!=%d" % (table.count(),
                                                            table2.count())



    def test_pagination(self):
        add_n_test_users(10)
        table = AdminTable(User.objects.all())
        table.rows_per_page = 5
        assert table.count()==10
        assert len(list(table.rows()))==5, len(list(table.rows()))

        table = AdminTable(User.objects.all())
        table.rows_per_page = 3
        assert table.has_previous_page() == False
        assert table.has_next_page() == True
        assert table.previous_page_number() == 1
        assert table.next_page_number() == 2
        assert len(list(table.rows()))==3, len(list(table.rows()))

        table = AdminTable(User.objects.all())
        table.rows_per_page = 3
        table.current_page = 4
        assert table.previous_page_number() == 3
        assert table.next_page_number() == 4, table.next_page_number()
        assert table.has_previous_page() == True
        assert table.has_next_page() == False
        assert len(list(table.rows()))==1, len(list(table.rows()))

        table = AdminTable(User.objects.all())
        table.rows_per_page = 3
        table.current_page = 5 # out of index
        assert table.current_page == 4, table.current_page # set to last page
        assert len(list(table.rows()))==1, len(list(table.rows()))
        assert table.has_previous_page() == True
        assert table.has_next_page() == False

        assert table.page_index()==[1, 2, 3, 4], table.page_index()

        table.rows_per_page = 10
        assert table.page_index()==[1, 2, 3, 4], table.page_index()

        table.rows_per_page = 5
        assert table.page_index()==[1,2,3,4], table.page_index()

        table.rows_per_page = 4
        assert table.page_index()==[1, 2, 3, 4], table.page_index()



    def test_search(self):
        # <QueryDict: {u'registered:datetime:lastmonth': [u'2009-03-05---2009-04-05'], u'id:integer AUTO_INCREMENT:null': [u'true'], u'id:integer AUTO_INCREMENT:eq': [u'1'], u'registered:datetime:period': [u'YYYY-MM-DD---YYYY-MM-DD'], u'id:integer AUTO_INCREMENT:lte': [u'2'], u'registered:datetime:lastweek': [u'2009-03-29---2009-04-05'], u'registered:datetime:lastday': [u'2009-04-05---2009-04-05'], u'deleted:bool:null': [u'true'], u'registered:datetime:dtequal': [u'YYYY-MM-DD'], u'registered:datetime:lastyear': [u'2008-04-05---2009-04-05'], u'deleted:bool:true': [u'true'], u'action': [u'start_search'], u'registered:datetime:null': [u'true'], u'id:integer AUTO_INCREMENT:gte': [u'3'], u'registered:datetime:since': [u'YYYY-MM-DD'], u'deleted:bool:false': [u'false'], u'registered:datetime:before': [u'YYYY-MM-DD']}>

        add_n_test_users(10)
        table = AdminTable(User.objects.all())
        request = FakeRequest()
        assert table.searchable_fields()[0].name=='id', table.searchable_fields()

        def check_contains():
            """ field__contains """
            request.GET.setlist('username:varchar(32):like',['username'])
            request.GET['action']='start_search'
            request.GET['table']=table.name
            table.process_request(request)
            assert table.settings.search_rules==[('and', u'username', 'like', u'username')], table.settings.search_rules
            rows = len(list(table.rows()))
            assert rows==10, rows

        def check_equal2():
            """ field=value """
            request.GET.setlist('username:varchar(32):eq',['0username', '1username'])
            request.GET['action']='start_search'
            request.GET['table']=table.name
            table.process_request(request)
            assert table.settings.search_rules==[('and', None, None, [('or', u'username', 'eq', u'0username'), ('or', u'username', 'eq', u'1username')])], table.settings.search_rules
            rows = len(list(table.rows()))
            assert rows==2, rows

        def check_equal1():
            """ field=value """
            request.GET.setlist('username:varchar(32):eq',['0username'])
            request.GET['action']='start_search'
            request.GET['table']=table.name
            table.process_request(request)
            rows = len(list(table.rows()))
            assert rows==1, rows

        def check_not_equal():
            request.GET.setlist('username:varchar(32):ne',['0username'])
            request.GET['action']='start_search'
            request.GET['table']=table.name
            table.process_request(request)
            rowscount = len(list(table.rows()))
            assert rowscount==9, rowscount



        def check_equal0():
            """ field=value """
            request.GET.setlist('username:varchar(32):eq',['non-existing-username'])
            request.GET['action']='start_search'
            request.GET['table']=table.name
            table.process_request(request)
            rows = len(list(table.rows()))
            assert rows==0, rows


        def check_integer_exact():
            assert table.searchable_fields()[0].name=='id', table.searchable_fields()
            request = FakeRequest()
            request.GET['id:integer AUTO_INCREMENT:eq']='2'
            request.GET['action']='start_search'
            request.GET['table']=table.name
            table.process_request(request)
            assert table.settings.search_rules==[('and', u'id', 'eq', u'2')], table.settings.search_rules
            rows = len(list(table.rows()))
            assert rows==1, rows


        def check_integer_min():
            assert table.searchable_fields()[0].name=='id', table.searchable_fields()
            request = FakeRequest()
            request.GET['id:integer AUTO_INCREMENT:lte']='2'
            request.GET['action']='start_search'
            request.GET['table']=table.name
            table.process_request(request)
            assert table.settings.search_rules==[('and', 'id', 'lte', '2')], table.settings.search_rules
            rows = len(list(table.rows()))
            assert rows==2, rows


        def check_integer_max():
            assert table.searchable_fields()[0].name=='id', table.searchable_fields()
            request = FakeRequest()
            request.GET['id:integer AUTO_INCREMENT:gte']='2'
            request.GET['action']='start_search'
            request.GET['table']=table.name
            table.process_request(request)
            assert table.settings.search_rules==[('and', 'id', 'gte', '2')], table.settings.search_rules
            rows = len(list(table.rows()))
            assert rows==9, rows


        def check_date_since0():
            request = FakeRequest()
            request.GET['last_login:datetime:since']='2228-01-01'
            request.GET['action']='start_search'
            request.GET['table']=table.name
            table.process_request(request)
            assert table.settings.search_rules==[('and', u'last_login', 'gte', u'2228-01-01')], table.settings.search_rules
            rows = len(list(table.rows()))
            assert rows==0, rows

        def check_date_since10():
            request = FakeRequest()
            request.GET['last_login:datetime:since']=datetime.date.today().isoformat()
            request.GET['action']='start_search'
            request.GET['table']=table.name
            table.process_request(request)
            assert table.settings.search_rules==[('and', u'last_login', 'gte', datetime.date.today().isoformat())], table.settings.search_rules
            rows = len(list(table.rows()))
            assert rows==10, rows

        def check_date_before0():
            request = FakeRequest()
            request.GET['last_login:datetime:before']='2228-01-01'
            request.GET['action']='start_search'
            request.GET['table']=table.name
            table.process_request(request)
            assert table.settings.search_rules==[('and', u'last_login', 'lte', u'2228-01-01')], table.settings.search_rules
            rows = len(list(table.rows()))
            assert rows==10, rows

        def check_date_before10():
            request = FakeRequest()
            request.GET['last_login:datetime:before']=datetime.date.today().isoformat()
            request.GET['action']='start_search'
            request.GET['table']=table.name
            table.process_request(request)
            assert table.settings.search_rules==[('and', u'last_login', 'lte', datetime.date.today().isoformat())], table.settings.search_rules
            rows = len(list(table.rows()))
            assert rows==0, rows

        def check_date_period10():
            request = FakeRequest()
            today=datetime.date.today().isoformat()
            request.GET['last_login:datetime:period']="%s---%s" % (today, today)
            request.GET['action']='start_search'
            request.GET['table']=table.name
            table.process_request(request)
            rows = len(list(table.rows()))
            assert rows==0, rows

        def check_isnull():
            request = FakeRequest()
            today=datetime.date.today().isoformat()
            request.GET['last_login:datetime:null']="true"
            request.GET['action']='start_search'
            request.GET['table']=table.name
            table.process_request(request)
            assert table.settings.search_rules==[('and', u'last_login', 'isnull', u'')], table.settings.search_rules
            rows = len(list(table.rows()))
            assert rows==0, rows

        def check_bool():
            request = FakeRequest()
            today=datetime.date.today().isoformat()
            request.GET['is_staff:bool:true']="true"
            request.GET['action']='start_search'
            request.GET['table']=table.name
            table.process_request(request)
            assert table.settings.search_rules==[('and', u'is_staff', u'bool', u'true')], table.settings.search_rules
            rows = len(list(table.rows()))
            assert rows==0, rows




        tests = [check_equal2, check_equal1, check_contains, check_integer_exact,
                 check_integer_min, check_integer_max, check_date_since0, check_date_since10,
                 check_date_before0, check_date_before10, check_date_period10,
                 check_isnull, check_bool, check_not_equal]


        for test in tests:
            table = AdminTable(User.objects.all()) # check ORM data source
            request = FakeRequest()
            test()

            ds = DataSource()
            ds.set_tables('auth_user')
            ds.set_columns(user_columns())
            table = AdminTable(ds) # check custom data source
            test()

    def test_shown_columns(self):
        add_n_test_users(10)
        request = FakeRequest()
        table = AdminTable(User.objects.all())
        table.set_shown_columns(('id', 'username', 'first_name', 'last_name'))
        assert len(list(table.rows())[0])==4

    def test_request(self):
        add_n_test_users(10)
        request = FakeRequest()
        table = AdminTable(User.objects.all())
        table.rows_per_page = 4

        request.GET['admintable_page']=2
        table.process_request(request)
        assert table.current_page==2, table.current_page

        request = FakeRequest()
        request.GET['admintable_page']=3
        table.process_request(request)
        assert table.current_page==3

        request.GET['set_admintable_page']='http://some.spammers.site/'
        table.process_request(request)
        assert table.current_page==3
        table.extvars='somekey=true'
        assert table.getvars().find('somekey=true')!=-1,table.getvars()


    def test_save_preferences(self):
        add_n_test_users(10)

        # testing save preferences (to session). change
        # some preference, and then read on next request
        request = FakeRequest()
        table = AdminTable(User.objects.all())
        table.rows_per_page = 4
        table.process_request(request)


        for name,value in table.getvars_list():
            request.GET[name]=value
        table = AdminTable(User.objects.all())
        table.process_request(request)

        assert len(list(table.rows()))==4
        assert len(list(AdminTable(User.objects.all()).rows()))==10

        # now, test saving to database and then seeing that default
        # has changed
        table = AdminTable(User.objects.all())
        table.name = 'setprefstable'
        request.method = 'POST'
        request.GET['action']='preferences'
        request.GET['table']=table.name
        request.POST['saveas']='default'
        request.POST.setlist('shown_columns',['id','username','first_name','last_name',
                                              'last_login'])
        request.POST['rows_per_page']='2'
        request.POST['current_page']='2'
        request.POST['sort_on'] = 'None'
        table.process_request(request)

        assert len(list(table.rows()))==2
        table = AdminTable(User.objects.all())
        table.name = 'setprefstable'
        table.process_request(FakeRequest())
        assert len(list(table.rows()))==2

        # save search
        request = FakeRequest()
        table = AdminTable(User.objects.all())
        table.name = 'searchtest'
        request.META['PATH_INFO'] = '/%s/' % table.name
        request.GET['saveas'] = '5user'
        request.GET['action'] = 'start_search'
        request.GET['table'] = table.name
        request.GET['username:varchar(29):like'] = '5user'
        table.process_request(request)
        assert len(list(table.rows()))==1

        # try to restore config
        request = FakeRequest()
        table = AdminTable(User.objects.all())
        table.name = 'searchtest'
        request.META['PATH_INFO'] = '/%s/' % table.name
        request.GET['restore']='5user-'
        table.process_request(request)
        assert len(list(table.rows()))==1

    # def simplest_possible_usage_scenario(self):
    #     table = AdminTable(User.objects.all())
    #     table.process_request(request)
    #     if table.has_direct_response:
    #         return table.response # this is for CSV, XML, AJAX calls
    #     return direct_to_template(request, 'somefile.html', dict(table=table))

    # def use_case_from_model(self):
    #     from django.contrib.user.models import User
    #     from hdg.djangoapps.dbtable import AdminTable, DataSource
    #     data_source = DataSource.from_model(User)
    #     table = DBTable.from_model(User)
    #     table.set_source(data_source)
    #     table.process_request(request)
    #     if table.has_direct_response:
    #         return table.response # this is for CSV, XML, AJAX calls
    #     return direct_to_template(request, 'somefile.html', dict(table=table))


    # def use_cases_sampleView(self):
    #     from hdg.djangoapps.dbtable.models import DBTable
    #     from django.db import models

    #     class DataSource(object):
    #         def run_query(): pass
    #         def columns(): pass # names and labels
    #         def column_names(): pass
    #         def total(): pass
    #         def get_slice(record, n_records): pass
    #         def show_query(): pass


    #     class UserManager(DBTable):
    #         id = models.AutoField(db_column='ID',primary_key=True)
    #         username = models.CharField(max_length=20)
    #         password = models.CharField(max_length=20)

    #         class Settings:
    #             rows_per_page = 10
    #             do_not_sort_on = ('username',)
    #             do_not_search_on = ('password',)
    #             allow_search = False
    #             allow_filter = False
    #             allow_save_state = False
    #             select_related = True
    #             fetch_related = ('group',)



    #     request = {}
    #     table = UserManager(request)
    #     table.columns
    #     table.rows
    #     for row in table.lines:
    #         pass
    #     table.pages
    #     table.rows_per_page
    #     table.current_page
    #     table.next_page
    #     table.prev_page
    #     table.searchable_fields
    #     table.sortable_fields
    #     table.is_sortable_field('username')
    #     table.is_searchable_field('password')
    #     table.get_row(row_id)
    #     table.update_row(row_id)
    #     if table.direct_response:
    #         return table.response
    #     table.url
    #     table.pages_list
    #     # format for every field???
    #     table.set_rows_per_page


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(AdminTableTest),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
    # add_n_test_users(1000)

