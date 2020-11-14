import pickle
import datetime

from django.db import models, connection
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User, AnonymousUser
from django.utils.translation import ugettext_lazy as _


DEFAULT_TABLE_SETTINGS = dict(rows_per_page = 15,
                              current_page = 1,
                              name = 'admintable',
                              extvars = '',
                              page_index_steps=3,
                              search_enabled = True,
                              reordering_enabled = True,
                              csv_export_enabled = True,
                              preferences_enabled = True,
                              export_enabled = True,
                              search_rules = [],
                              shown_columns=[],
                              sort_on = None,
                              sort_reverse = False,
                              )

def _int_or_none(d):
    """ Helper function to return interger or None. """
    try:     return int(d)
    except:  return None


def realuser(user):
    return user if (user and user.is_authenticated) else None


def _apply_filters(data, filters):
    """ Importing filters module, applying filter. See http://docs.djangoproject.com/en/dev/ref/templates/builtins/ for more information on filters. """
    for filtername, args, module in filters:
        exec('import %s as fl' % module)
        data = getattr(fl, filtername)(data, args)
    return data

def _addarg(qargs, andor, newrule):
    q = None
    if qargs is None:
        if andor=='ne':
            q = ~Q(**newrule)
        else:
            q = Q(**newrule)
    elif andor=='and':
        q = qargs & Q(**newrule)
    elif andor=='or':
        q = qargs | Q(**newrule)
    elif andor=='ne':
        q = qargs & ~Q(**newrule)
    assert q is not None
    return q


def _make_sql(rules):
    condition = ''
    args = []
    firstrule = True
    for andor, field, op, value in rules:
        if field is None:
            cond1, args1 = _make_sql(value)
            if not firstrule:
                condition += ' '+andor
            condition += ' ' + cond1
            args += args1
        else:
            if not firstrule:
                condition += ' ' + andor + ' '
            if op=='eq':
                if andor=='ne':
                    condition += '%s<>' % field
                else:
                    condition += '%s=' % field
                condition += '%s'
                args.append(value)
            elif op=='like':
                condition += '%s like ' % field
                condition += '%s'
                args.append('%'+value+'%')
            elif op=='lte':
                condition += '%s<=' % field
                condition += '%s'
                args.append(value)
            elif op=='gte':
                condition += '%s>=' % field
                condition += '%s'
                args.append(value)
            elif op=='isnull':
                condition += '%s is null' % field
            elif op=='bool':
                if value=='true':
                    condition += '%s=1' % field
                else:
                    condition += '%s=0' % field

        firstrule = False
    return condition, args

def _make_query(rules):
    qargs = None
    for andor, fieldname, op, value in rules:
        if op=='eq':
            qargs = _addarg(qargs, andor, {str(fieldname):value})
        elif op == 'gte':
            if value=='midnight':
                value = datetime.date.today().isoformat()+' 00:00'
            elif value.find('m')!=-1 or value.find('d')!=-1 \
                   or value.find('h')!=-1 \
                   or value.find('w')!=-1 or value.startswith('-'):

                if value.find('m')!=-1:
                    value=value.replace('m','') # minutes
                    minus = datetime.timedelta(minutes=abs(int(value)))
                elif value.find('h')!=-1:
                    value=value.replace('h','') # hours
                    minus = datetime.timedelta(hours=abs(int(value)))
                elif value.find('w')!=-1:
                    value=value.replace('w','') # weeks
                    minus = datetime.timedelta(weeks=abs(int(value)))
                else:
                    value=value.replace('d','') # days
                    minus = datetime.timedelta(days=abs(int(value)))

                value=(datetime.datetime.now()-minus).strftime('%Y-%m-%d %H:%m')
            qargs = _addarg(qargs, andor, {str('%s__gte' % fieldname): value})
        elif op == 'lte':
            qargs = _addarg(qargs, andor, {str('%s__lte' % fieldname): value})
        elif op == 'like':
            qargs = _addarg(qargs, andor, {str('%s__contains' % fieldname): value})
        elif op is None:
            if qargs is None:
                qargs = _make_query(value)
            elif andor=='and':
                qargs = qargs & _make_query(value)
            else:
                qargs = qargs | _make_query(value)
        elif op=='isnull':
            qargs = _addarg(qargs, andor, {str('%s__isnull' % fieldname): True})
        elif op=='bool':
            if value=='true':
                qargs = _addarg(qargs, andor, {str(fieldname): True})
            else:
                qargs = _addarg(qargs, andor, {str(fieldname): False})
        elif op=='ne':
            qargs = _addarg(qargs, andor, {str(fieldname):value})
        else:
            print('apply_search: rule not applied: %s-%s' % (andor, op))
    return qargs


class Settings(object):  # dict with strict checking of variable name
    """ Difference from Storage and Dict is that this using that class
    makes sure we don't mistype the variable name and use only predefined
    variables. So, while allowing easy access in dot-style to contents,
    this class does name checks."""
    def __init__(self):
        for key in DEFAULT_TABLE_SETTINGS.keys():
            setattr(self, key, DEFAULT_TABLE_SETTINGS[key])

    def __setattr__(self, name, value):
        assert name in DEFAULT_TABLE_SETTINGS.keys()
        super(Settings, self).__setattr__(name, value)

    def __str__(self):
        s = ''
        for k in DEFAULT_TABLE_SETTINGS.keys():
            s += "settings %s=%s\n" % (k, getattr(self,k))
        return s


class Storage(object):
    """ Used by Settings object. Container for a name=value settings. """
    def __init__(self, dict=None):
        if dict:
            for k in dict.keys():
                setattr(self,k,dict[k])

class GeneratedColumn(object):
    """ Inherit from Generated column, override `render` method to make
    custom table column. """
    def __init__(self, name, label=None, renderfunc=None):
        self.name = name
        if label:
            self.label = label
        else:
            self.label = name
        self._render = renderfunc

    def render(self, row):
        if self._render:
            return self._render(row)
        else:
            return '--generated column %s--' % self.name


class AdminTableConfig(models.Model):
    """ End users can store individual table configuration here. This is used
    to save searches, save screen settings, and everything else stored in
    self.settings object of Table"""
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(_('Name'), max_length=50)
    config = models.TextField(_('Config'), default='')
    url = models.CharField(_('URL'), max_length=256)
    is_public = models.BooleanField(_('Is Public'), default=False)

    def __unicode__(self):
        return u'%s-%s' % (self.user,
                           self.name)

    def needs_custom_data(self):
        settings = pickle.loads(eval(str(self.config)))
        for key in settings.search_rules:
            if key[3].find('%s')!=-1:
                return True
        return False

    def variables(self):
        return pickle.loads(eval(str(self.config)))

    class Meta:
        db_table = 'admin_table_config'
        verbose_name = _(u"Admin Table config")
        verbose_name_plural = _(u"Admin Table configs")



class AdminTable(object):
    """ AdminTable is main central object of the module. It connects DataSource with results data. """
    def __init__(self, data_source=None, request=None, **kwargs):
        self.request = request
        self.has_direct_response = False
        self.data_source = data_source
        self._columns = [(f.name, f.verbose_name)
                         for f in self.data_source.model._meta.fields]
        self._sortable_columns = [('None','None')]+self._columns
        self._shown_columns = None
        self._count = None
        self.settings = Settings()
        self._fields = {}
        self._searchable_fields = []
        self._sid = None
        self._applied_search = None
        self._actions = []
        self._controls = []
        self._PATH_INFO = None
        self.user = None
        self.column_filters = {}
        self.columns_css = {}
        self.action_processors = {}

        for f in self.data_source.model._meta.fields:
            self._fields[f.name]=f
            self._searchable_fields.append( f )
            dbtype=f.db_type(connection=connection)
            if dbtype=='integer' or dbtype[7:]=='numeric':
                self.columns_css[f.name]='num'

    def add_action_processor(self, name, funcref):
        self.action_processors[name]=funcref

    def verboose_column_name(self, column_name):
        for c in self._columns:
            if c[0]==column_name:
                return c[1]
        return None

    def path_info(self):
        return self._PATH_INFO

    def configured_filters(self):
        """ Returns list of configured filtes, just their names from AdminTableConfig.name"""
        filters = []
        rules = Q(is_public=True)

        if not self.user.is_anonymous():
            rules |= Q(user=self.user)
        else:
            rules |= Q(user=None)


        for tc in AdminTableConfig.objects.filter(rules).exclude(name='default'):
            if tc.url == self._PATH_INFO:
                filters.append(tc)
        return filters

    def append_column_filter(self, column, filter, arg, module='django.template.defaultfilters'):
        """ Appends filter function from module `module`. """
        current_filters = self.column_filters.get(column, [])
        current_filters.append( (filter, arg, module) )
        self.column_filters[column] = current_filters

    def get_sortable_columns(self):
        """ Returns list of sortable columns for table """
        return self._sortable_columns
    sortable_columns = property(get_sortable_columns)

    def set_sort_on(self, field):
        """ Set sort on field """
        if field != 'None' and field in [f[0] for f in self.sortable_columns]:
            if self.settings.sort_on == field:
                self.settings.sort_reverse = not self.settings.sort_reverse
            self.settings.sort_on = field
        else:
            self.settings.sort_on = None

    def set_sort_reverse(self, value):
        """ Reverse current sort """
        if value:
            self.settings.sort_reverse = True
        else:
            self.settings.sort_reverse = False


    def search_rules_list(self, lst=None):
        res = []

        if not lst:
            lst = self.settings.search_rules

        for andor, fieldname, op, value in lst:
            if fieldname is None:
                res += self.search_rules_list(value)
            else:
                try:    value1, value2  = value.split('---')
                except: value1 = value2 = value
                combined_fieldname = "%s:%s" % (fieldname,
                                                self._fields[fieldname].db_type(connection=connection))
                condition_title=op
                if self._fields[fieldname].db_type(connection=connection)=='datetime':
                    if    op=='lte':
                        condition_title='Before'
                        op='before'
                    elif  op=='gte':
                        condition_title='Since'
                        op='since'
                elif  op=='lte': condition_title='< Less Then'
                elif  op=='gte': condition_title='> Greater Then'
                elif  op=='eq':  condition_title='= Equal'
                if op=='isnull': op='null'
                if andor=='ne':
                    op='ne'
                    condition_title='Not Equal'
                res.append(dict(field_name=combined_fieldname,
                                field_title=self._fields[fieldname].verbose_name,
                                condition_value=op, condition_title=condition_title,
                                value1=value1, value2=value2))
        return res

    def save_user_preferences(self, request):
        """ Stores user preferences for current table object to session.
        This function is called automatically during table.process_request
        call. """
        session_key = 'tbl_%s_%s' %  (self.settings.name, self.sid(request))
        request.session[session_key] = self.settings


    def read_preferences_from_session(self, request):
        session_key = 'tbl_%s_%s' %  (self.settings.name, self.request_sid(request))
        if session_key in request.session:
            self.settings = request.session[session_key]

    def read_preferences_from_db(self, configname, request):
        username = None
        if '-' in configname:
            configname, username = configname.split('-')
        user = request.user
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                pass
        try:
            tc = AdminTableConfig.objects.get(name = configname,
                                              user = realuser(user),
                                              url = request.META['PATH_INFO'])
            self.settings = pickle.loads(eval(str(tc.config)))
        except AdminTableConfig.DoesNotExist:
            pass

    def restore_user_preferences(self, request):
        """ Restore user preferences from configuration saved in database.
        This function is called automatically during table.process_request
        call if 'restore' paramters is found.. """

        restoreconfig = None
        if self.request_sid(request):
            self.read_preferences_from_session(request)
        else:
            restoreconfig = 'default-'

        if 'restore' in request.GET:
            restoreconfig = request.GET.get('restore')

        if restoreconfig:
            self.read_preferences_from_db(restoreconfig, request)


    def add_control(self, url, title):
        """ 'control' is a button above/below table, which affects the
        whole results set. The example of "Control" button would be
        the link to Django-admin list of same objects."""
        self._controls.append(dict(url=url,
                                   title=title))

    def custom_controls(self):
        """ Return full list of table controls for the current table'"""
        return self._controls

    def column_names(self):
        """ Return list of column names """
        return [name for name,lable in self._columns]

    def add_column(self, column, index=None):
        """ Usually used to add GeneratedColumn, or to specify columns
        list for raw SQL query """
        col = (column.name, column.label)
        if index is not None:
            self._columns.insert(index, col)
        else:
            self._columns.append(col)

        self._fields[column.name]=column


    def add_action(self, label, link):
        """ At the right side of table we usually have "Action" column.
        `add_control` is used to add more actions."""

        self._actions.append((label, link))

    def add_action_column(self):
        """ This is helper function, so instead of inheriting/overriding
        GeneratedField every time we need an Action column, we can add
        it by calling this fuction. See also: add_action() """
        def renderfunc(row):
            actions='<ul class="actions">\n'
            for label,link in self._actions:
                argsdict = {}
                for col in self.column_names():
                    try:
                        argsdict[col]=getattr(row,col)
                    except:
                        argsdict[col]=''
                link = link % argsdict
                actions+= '<li><a href="%s">%s</a></li>\n' % (link, label)
            actions+='</ul>\n'
            return mark_safe(actions)
        self.add_column(GeneratedColumn('action', renderfunc=renderfunc))


    def add_select_column(self):
        """ This is helper function, so instead of inheriting/overriding
        GeneratedField every time we need an Action column, we can add
        it by calling this fuction. See also: add_action() """
        def renderfunc(row):
            s='<input type="checkbox" class="select-checkbox" id="id-row-%s" '\
               'name="id-row-%s">' % (row.id,
                                      row.id,)

            return mark_safe(s)
        self.add_column(GeneratedColumn('select', ' ', renderfunc=renderfunc), 0)
        self.columns_css['select']='selchk'

    def searchable_fields(self):
        """ Returns list of searchable fields. Field: db.models.field """
        return self._searchable_fields


    def set_name(self, name):
        """ Set table name. This is required for the cases when we have multiple
        table objects on same screen """
        self.settings.name = name

    def get_name(self):
        """ Returns this table name for reference """
        return self.settings.name
    name = property(get_name, set_name)

    def getvars_list(self):
        return [x.split('=') for x in self.getvars().split('&')]

    def getvars(self):
        """         This function output should be included to every link on a page,
        so current table state is not lost. """
        getvars = {}
        # external variables work as defaults, but filter out this table
        # references because we reset them from object
        if self.settings.extvars:
            for nameval in self.settings.extvars.split('&'):
                name,val = nameval.split('=')
                if name=='table': continue
                if name.startswith("%s_" % self.settings.name): continue
                getvars[name] = val

        # add this table variables
        getvars['table'] = self.settings.name
        getvars['%s_page' % self.settings.name ] = self.settings.current_page
        getvars['%s_sid' % self.settings.name] = self._sid

        return '&'.join(['%s=%s' % (n,v) for n,v in getvars.iteritems()])

    def get_extvars(self): return self.settings.extvars
    def set_extvars(self, extvars): self.settings.extvars = extvars
    extvars = property(get_extvars, set_extvars)

    def get_current_page(self):
        """ Current rendered page """
        return self.settings.current_page

    def set_current_page(self, page):
        """ Jump to page `page` """
        try:
            page=int(page)
        except:
            return
        if page>self.pages():
            self.settings.current_page = self.pages()
        elif page>0:
            self.settings.current_page=page

    current_page=property(get_current_page, set_current_page)


    def get_rows_per_page(self):
        """ Current setting of rows per page """
        return self.settings.rows_per_page

    def set_rows_per_page(self, value):
        """ Set rows per page """
        self.settings.rows_per_page = value

    rows_per_page = property(get_rows_per_page, set_rows_per_page)


    def has_previous_page(self):
        if self.settings.current_page > 1:
            return True
        return False

    def has_next_page(self):
        if self.settings.current_page<self.pages():
            return True
        return False

    def previous_page_number(self):
        prev = self.settings.current_page - 1
        if prev<=1: prev=1
        return prev

    def next_page_number(self):
        next = self.settings.current_page + 1
        if next>self.pages():
            next = self.pages()
        return next

    def columns(self):
        """ Returns list of all table columsn in format of name,label """
        return self._columns

    def shown_columns(self):
        """ Only shown columns in format name,label """
        if self.settings.shown_columns:
            return self.settings.shown_columns
        return self.columns()

    def shown_columns_metainfo(self):
        res=[]
        for name,label in self.shown_columns():
            res.append(dict(name=name,
                            label=label,
                            is_sortable = (name,label) in self.sortable_columns,
                            ))
        return res


    def columns_metainfo(self):
        """ List. Every list item is dictionary: name, label, is_shown"""
        shown_column_names = [name for name,label in self.shown_columns()]
        res=[]
        for name,label in self.columns():
            res.append(dict(name=name,
                            label=label,
                            is_shown = name in shown_column_names))
        return res

    def set_shown_columns(self, column_names):
        """ Specify list of column names to be shown. """
        self.settings.shown_columns=[]
        #for name,label in self.columns():
        #    if name in column_names:
        #        self.settings.shown_columns.append( (name, label) )
        for n in column_names:
            for name,label in self.columns():
                if n==name:
                    self.settings.shown_columns.append( (name, label) )

    def pages(self):
        """ Calculate amount of results pages."""
        pages = full_pages = self.count()/self.settings.rows_per_page
        if full_pages * self.settings.rows_per_page < self.count():
            pages += 1
        return pages

    def page_index(self):
        """ Helper function for paginator - shows page range to choose """
        res = []
        if self.pages()==0:
            return []
        res.append(1)
        res.append(self.pages())
        for i in range(self.settings.current_page+1,
                       self.settings.current_page+self.settings.page_index_steps):
            if i<self.pages():
                res.append(i)

        for i in range(self.settings.current_page,
                       self.settings.current_page-self.settings.page_index_steps, -1):
            if i>1:
                res.append(i)

        res = list(set(res))
        res.sort()
        if len(res)<2: return []
        return res

    def all_source_rows(self):
        """ This is actually the main method to fetch data. It applies
        filter, counts results, fetches results for current page. Normally
        called from template."""

        for row in self.data_source:
            yield row

    def rows_plain(self, limit_current_page=True):

        if not self._applied_search:
            self._apply_search()

        if limit_current_page:
            r_start = (self.settings.current_page-1)*self.settings.rows_per_page
            if r_start<0: r_start=0
            r_end = r_start+self.settings.rows_per_page
            data_slice = self.data_source[r_start:r_end]
            data_source = data_slice
        else:
            data_source = self.data_source

        for row in data_source:
            r=[]
            for colname,colobj in self.shown_columns():
                column = {}
                field = self._fields[colname]

                if colname in ['select', 'action']:
                    continue

                if hasattr(field, 'render'):
                    column['data'] = field.render(row)
                else:
                    column['data'] = getattr(row,colname)

                if colname in self.column_filters:
                    column['data'] = _apply_filters(column['data'], self.column_filters[colname])

                r.append(column)

            yield r

    def rows(self):
        """ This is actually the main method to fetch data. It applies
        filter, counts results, fetches results for current page. Normally
        called from template."""
        if not self._applied_search:
            self._apply_search()

        r_start = (self.settings.current_page-1)*self.settings.rows_per_page
        if r_start<0: r_start=0
        r_end = r_start+self.settings.rows_per_page
        data_slice = self.data_source[r_start:r_end]

        for row in data_slice:
            r=[]
            for colname,colobj in self.shown_columns():
                column = {}
                column['css_class']=self.columns_css.get(colname,'')
                field = self._fields[colname]

                if hasattr(field, 'render'):
                    column['data'] = field.render(row)
                else:
                    column['data'] = getattr(row,colname)

                if colname in self.column_filters:
                    column['data'] = _apply_filters(column['data'], self.column_filters[colname])

                r.append(column)

            yield r


    def sid(self, request):
        """ Returns unique Session ID for this table screen. Purpose: you can
        open same table in different configurations in multiple browser windows
        and still be able to work: session keys don't override each other."""
        if '%s_sid' % self.settings.name in request.GET:
            sid = request.GET['%s_sid' % self.settings.name]
        elif self._sid:
            sid = self._sid
        else:
            sid = None
        #print self.settings.name, request.GET, sid
        return sid

    def _generate_sid(self):
        """ Generate unique Session ID for this table """
        import time
        return str(int(time.time()*10))[-7:]

    def request_sid(self, request):
        return request.GET.get('%s_sid' % self.settings.name, None)

    def save_config(self, request, name):
        tc, c = AdminTableConfig.objects.get_or_create(url = request.META['PATH_INFO'],
                                                       user = realuser(request.user),
                                                       name = name)
        tc.config = repr(pickle.dumps(self.settings))
        tc.save()


    def process_request(self, request):
        """ This method should be called from your view to process any
        user input. Also please do necessary check:
        if table.has_direct_response: return table.response() for
        the cases when table have direct answer to user actions """

        self._PATH_INFO = request.META['PATH_INFO']
        self.user = request.user

        # set current page number
        set_page_n = None
        spvar = 'set_%s_page' % self.settings.name
        spvar1 = '%s_page' % self.settings.name
        set_page_n = request.POST.get(spvar,
                     request.GET.get(spvar,
                     request.POST.get(spvar1,
                     request.GET.get(spvar1,
                     None))))

        self.restore_user_preferences(request)

        self._sid = self.request_sid(request)
        if not self._sid:
            self._sid = self._generate_sid()

        newsearchrules=[]

        for r in self.settings.search_rules:
            r=list(r)
            if type(r[3])!=type([]) and r[3].find('%s') != -1:
                if 'action' in request.GET and request.GET['action']=='quicksearch':
                    r[3] = request.GET.get(r[1])
                else:
                    from hdg.djangoapps.admintable.views import quicksearch_form
                    self._response = quicksearch_form(request, self)
                    self.has_direct_response = True
            newsearchrules.append(r)
        if 'action' in request.GET and request.GET['action']=='quicksearch':
            self.settings.search_rules = newsearchrules

        if request.GET.get('action')=='set_sort_on'\
            and request.GET.get('fieldname','') in self._fields:
            self.set_sort_on(request.GET['fieldname'])

        if 'action' in request.GET and self.name == request.GET['table']:
            if request.GET['action'] in ['search', 'start_search', 'editfilter']:
                if request.GET['action']=='start_search':
                    self._save_new_search_rules(request)
                if request.GET.get('saveas',''):
                    self.save_config(request, request.GET.get('saveas'))
                if request.GET['action'] in ['search', 'editfilter'] \
                       or request.GET.get('saveas',''):
                    from hdg.djangoapps.admintable.views import search_form
                    self._response = search_form(request, self)
                    self.has_direct_response = True
            elif request.GET['action']=='reset':
                self.settings.search_rules = []
            elif request.GET['action'] == 'preferences':
                from hdg.djangoapps.admintable.views import preferences_form
                self._response = preferences_form(request, self)
                self.has_direct_response = True
                if 'saveas' in request.POST and request.POST['saveas']!='none':
                    self.save_config(request, request.POST.get('saveas'))
            elif request.GET['action']=='runaction' and \
                 request.GET['runaction'] in self.action_processors:
                response = self.action_processors[request.GET['runaction']](self, request)
                if response:
                    self._response = response
                    self.has_direct_response = True
            elif request.GET['action']=='delete':
                try:
                    AdminTableConfig.objects.get(url = request.META['PATH_INFO'],
                                                 user = realuser(request.user),
                                                 id = request.GET.get('id')).delete()
                except AdminTableConfig.DoesNotExist:
                    print(
                        'does not exist',
                        request.META['PATH_INFO'],
                        realuser(request.user),
                        request.GET.get('name'))



        if set_page_n:
            self.set_current_page(set_page_n)


        self.save_user_preferences(request)


    def _apply_search(self):
        self._applied_search = True

        if self.settings.search_rules:
            if hasattr(self.data_source, 'where'):
                self.data_source = self.data_source.filter(self.settings.search_rules)
            else:
                q = _make_query(self.settings.search_rules)
                self.data_source = self.data_source.filter(q)
        if self.settings.sort_on:
            rev=''
            if self.settings.sort_reverse:
                rev='-'
            self.data_source = self.data_source.order_by(rev+self.settings.sort_on)

    def _save_new_search_rules(self, request):
        self.settings.search_rules = []
        for field in request.GET:
            try:
                fname, ftype, fop = field.split(':')
            except:
                continue

            modelfield = None
            for f in self.searchable_fields():
                if f.name==fname:
                    modelfield=f
                    break

            if fop=='eq':
                this_field_rules = []
                for fval in request.GET.getlist(field):
                    if modelfield.db_type(connection=connection)[:7] in ['varchar', 'integer']:
                        this_field_rules.append(('or',fname, 'eq', fval))
                if len(this_field_rules)==1:
                    self.settings.search_rules.append(('and',fname, 'eq', fval))
                else:
                    self.settings.search_rules.append(('and',None,None,this_field_rules))
            elif fop=='like':
                this_field_rules = []
                for fval in request.GET.getlist(field):
                    this_field_rules.append(('or',fname, 'like', fval))
                if len(this_field_rules)==1:
                    self.settings.search_rules.append(('and',fname, 'like', fval))
                else:
                    self.settings.search_rules.append(('and',None,None,this_field_rules))
            elif fop=='lte':
                this_field_rules = []
                for fval in request.GET.getlist(field):
                    this_field_rules.append(('or',fname, 'lte', fval))
                if len(this_field_rules)==1:
                    self.settings.search_rules.append(('and',fname, 'lte', fval))
                else:
                    self.settings.search_rules.append(('and',None,None,this_field_rules))
            elif fop=='gte':
                this_field_rules = []
                for fval in request.GET.getlist(field):
                    this_field_rules.append(('or',fname, 'gte', fval))
                if len(this_field_rules)==1:
                    self.settings.search_rules.append(('and',fname, 'gte', fval))
                else:
                    self.settings.search_rules.append(('and',None,None,this_field_rules))
            elif fop=='since':
                this_field_rules = []
                for fval in request.GET.getlist(field):
                    this_field_rules.append(('or',fname, 'gte', fval))
                if len(this_field_rules)==1:
                    self.settings.search_rules.append(('and',fname, 'gte', fval))
                else:
                    self.settings.search_rules.append(('and',None,None,this_field_rules))
            elif fop=='before':
                this_field_rules = []
                for fval in request.GET.getlist(field):
                    this_field_rules.append(('or',fname, 'lte', fval))
                if len(this_field_rules)==1:
                    self.settings.search_rules.append(('and',fname, 'lte', fval))
                else:
                    self.settings.search_rules.append(('and',None,None,this_field_rules))
            elif fop=='period':
                this_field_rules = []
                for fval in request.GET.getlist(field):
                    since, before = fval.split('---')
                    this_field_rules.append(('or',
                                             None,
                                             None,
                                             (
                        ('and',fname,'gte',since),
                        ('and',fname,'lte', before)
                        )))
                self.settings.search_rules.append(('and',None,None,this_field_rules))
            elif fop=='null':
                this_field_rules = []
                for fval in request.GET.getlist(field):
                    this_field_rules.append(('or',fname, 'isnull', ''))
                if len(this_field_rules)==1:
                    self.settings.search_rules.append(('and',fname, 'isnull', ''))
                else:
                    self.settings.search_rules.append(('and',None,None,this_field_rules))
            elif ftype=='bool':
                this_field_rules = []
                for fval in request.GET.getlist(field):
                    this_field_rules.append(('or', fname, ftype, fval))
                if len(this_field_rules)==1:
                   self.settings.search_rules.append(('and',fname, ftype, fval))
                else:
                   self.settings.search_rules.append(('and',None,None,this_field_rules))
            elif fop=='ne':
                this_field_rules = []
                for fval in request.GET.getlist(field):
                    if modelfield.db_type(connection=connection)[:7] in ['varchar', 'integer']:
                        this_field_rules.append(('or',fname, 'eq', fval))
                if len(this_field_rules)==1:
                    self.settings.search_rules.append(('ne',fname, 'eq', fval))
                else:
                    self.settings.search_rules.append(('ne',None,None,this_field_rules))



    def searchable_field_names(self):
        """ Returns list of searchable field names. Used in filter.html to render
        fields list which user can choose to search on """
        return [f.name for f in self.searchable_fields()]

    def response(self):
        """ Django HttpResponse object for cases when table have direct
        response """
        return self._response


    def render(self):
        """ Render table. Called from template. """
        from django.template import Context, loader, RequestContext

        t = loader.get_template('AdminTable/table.html')
        if self.request:
            c = RequestContext(self.request, {
                'table': self,
                })
        else:
            c = Context({
                'table': self,
                })
        return t.render(c)

    def count(self):
        """ Count amount of results. Applies search if not applied. """
        if not self._applied_search:
            self._apply_search()
        if not self._count:
            self._count = self.data_source.count()
        return self._count

    def export_tsv_unquote(self, table, request):
        from csv import QUOTE_NONE
        return self.export_tsv(table, request, quoting=QUOTE_NONE)

    def export_tsv(self, table, request, quoting=None):
        records = request.POST.getlist('record_id')
        from django.http import HttpResponse
        from cStringIO import StringIO
        import csv
        import types
        if quoting is None:
            quoting = csv.QUOTE_NONNUMERIC


        def dataline(r):
            data = []
            for f in r:
                df = f['data']
                if type(df) == types.UnicodeType:
                    df = df.encode('utf-8')
                data.append(df)
            return data

        def out(r):
            csvline_fh = StringIO()
            writer = csv.writer(csvline_fh, quoting=quoting, dialect='excel-tab')
            writer.writerow(dataline(r))
            csvline = csvline_fh.getvalue()
            csvline_fh.close()
            return csvline

        def gen_content():
            if len(records):
                for r in self.rows_plain():
                    if unicode(r[0]['data']) in records:
                        yield out(r)
            else:
                for r in self.rows_plain(limit_current_page=False):
                    yield out(r)

        response = HttpResponse(gen_content())
        response['Content-type'] = 'text/csv'
        response['Content-Disposition']= 'attachment; filename=records.csv'

        return response


class DataSource(object):
    """ Emulate QuerySet so we can alternatively
    use direct SQL query to build our table """

    def __init__(self): # , raw_sql_query, columns):
        self.model = Storage()
        self.model._meta = Storage()
        self.model._meta.fields = None
        self._count_expr = 'count(*)'
        self.where = []

    def set_tables(self, tables):
        self._tables = tables

    def set_columns(self, columns):
        self.model._meta.fields=[]
        for name,dbcolumn in columns:
            dbcolumn.name = name
            self.model._meta.fields.append(dbcolumn)

    def query(self):
        return 'select %s ' % '*' + self.query_right()

    def count(self):
        cursor = connection.cursor()
        qargs=[]
        for expr,argarr in self.where:
            qargs+=argarr
        cursor.execute('select %s ' % self._count_expr + self.query_right(), qargs)
        return int(cursor.fetchone()[0])


    def query_right(self):
        qr = 'from %s' % self._tables
        if len(self.where)>0:
            qr += ' where '+' and ' .join([expr for expr, arg in self.where])
        return qr



    def __getitem__(self, name):
        import types
        if type(name)== types.SliceType:
            from django.db import connection
            cursor = connection.cursor()

            query = self.query()+' limit %d, %d' % (name.start,name.stop-name.start)

            qargs = []
            for expr,argarr in self.where:
                qargs+=argarr
            if qargs: cursor.execute(query, qargs)
            else: cursor.execute(query)


            field_names = [c.name for c in self.model._meta.fields]
            while True:
                row = cursor.fetchone()
                if not row: break
                yield Storage(dict(zip(field_names, row)))


    def filter(self, q=None, **kwargs):
        if q:
            cond, args = _make_sql(q)
            self.where.append((cond, args))

        for kwarg in kwargs:
            if kwarg.endswith('__contains'):
                self.where.append((kwarg[:-10]+" like %s", ['%'+kwargs[kwarg]+'%']))
            elif kwarg.endswith('__gte'):
                self.where.append((kwarg[:-5]+" >= %s", [kwargs[kwarg]]))
            elif kwarg.endswith('__lte'):
                self.where.append((kwarg[:-5]+" <= %s", [kwargs[kwarg]]))
            else:
                print('ELSEEE')
                self.where.append(("%s=%s" % (kwarg, '%s'), [kwargs[kwarg]]))
        return self
