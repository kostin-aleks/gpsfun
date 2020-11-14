from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag('menu.html')
def show_menu():
    m = []

    m.append({'title': 'GPS-FUN admin',
             'submenu': [{'title': 'Home', 'url': '/gpsfun-admin/'},
                         #{'title': 'Django admin', 'url': '/gpsfun-admin/admin/'},
                         #{'title': 'Quick Filters', 'url': reverse('admin-table-prefs-list')},
                         #{'title': 'Other applications'},
                         #{'title': 'Teacher UI', 'url':'/teacher/'},
                         #{'title': 'Student UI', 'url':'/student/'},
                         ]})


    #m.append({'title': 'Users',
              #'submenu': [{'title': 'Students'},
                          #{'title': 'List', 'url': reverse('students-list')},
                          #{'title': 'Student Sets', 'url': reverse('students-studentset')},
                          #{'title': 'Event log', 'url': reverse('students-login-log')},
                          #{'title': 'Mentoring payments', 'url': reverse('mentoring-student-payments')},
                          #{'title': 'Teachers'},
                          #{'title': 'List', 'url': reverse('teachers-list')},
                          #{'title': 'Login log', 'url': reverse('teacher-login-log')},
                          #{'title': 'Mentoring payouts', 'url': reverse('mentoring-payouts')},
                          #{'title': 'Schools', 'url': '/YP-admin/admin/School/school/'},
                          #{'title': 'School search log', 'url': '/YP-admin/school/search_log/'},

                          #{'title': 'Support'},
                          #{'title': 'Contracts', 'url': '/YP-admin/admin/SupportContract/supportcontract/'},
                          #{'title': 'Messages', 'url': '/YP-admin/admin/MBoard/mboardthread/?section__exact=sgroup'},
                          #{'title': 'Mentoring questions', 'url': reverse('mentoring-questions')},

                          #{'title': 'Curators', 'url': reverse('curators-list')},
                          #]})


    #m.append({'title': 'Content',
              #'submenu': [{'title': 'Authoring groups', 'url': reverse('admin-agroup-list')},
                          #{'title': 'Courses', 'url': reverse('admin-course-list')},
                          #{'title': 'Course Reviews', 'url': reverse('admin-course-reviews')},
                          #{'title': 'Course Levels', 'url': reverse('admin-course-levels')},
                          #{'title': 'ORM Question Storage', 'url': '/YP-admin/admin/ORMQuestionStorage/'},
                          #{'title': 'ORM Quizzes', 'url': reverse('admin-orm-quiz-list')},
                          #{'title': 'Most popular ORM Quizzes', 'url': reverse('admin-pop-orm-quiz-list')},
                          #{'title': 'Quiz Response', 'url': reverse('quizresponse-list')},
                          #{'title': 'Student feedback', 'url': reverse('students-feedbacks')},

                          #{'title': 'Curriculums', 'url': '/YP-admin/admin/Curriculum/curriculum/'},
                          #{'title': 'Curriculums topics', 'url': '/YP-admin/topic/curriculums/'},

                          #{'title': 'Subjects level 1', 'url': '/YP-admin/admin/Subject/subjectlevel1/'},
                          #{'title': 'Subjects level 2', 'url': '/YP-admin/admin/Subject/subject/'},
                          #{'title': 'Subject Tags', 'url': '/YP-admin/admin/Subject/subjecttag/'},
                          #{'title': 'Topics', 'url': '/YP-admin/admin/Topic/topic/'},
                          #{'title': 'Tasks', 'url': reverse('admin-task-list')},
                          #{'title': 'Task results', 'url': reverse('admin-task-result-list')},
                          #{'title': 'Task export', 'url': reverse('task-export')},
                          #{'title': 'Task result page comments', 'url': reverse('task-result-page-comment')},
                          #{'title': 'Inbox messages', 'url': reverse('admin-inbox-message-list')},
                          #{'title': 'Assignmentsets', 'url': reverse('admin-aset-list')},
                          #{'title': 'Assignmentsets log stat', 'url': reverse('aset-list-log-usage')},
                          #{'title': 'Message Boards', 'url': '/YP-admin/admin/MBoard/'},
##                          {'title': 'Message Boards', 'url': reverse('admin-mboard-list')},
                          #{'title': 'Flash Games', 'url': '/YP-admin/admin/FlashGames/flashgame/'},
                          #{'title': 'Quiz Templates', 'url': reverse('quiztemplate-list')},
                          #{'title': 'Flash Avatars', 'url': '/YP-admin/admin/FlashAvatar/flashavatar/'},
                          #{'title': 'Grade Grids', 'url': reverse('admin-gradegrid-list')},
                          #{'title': 'Fuzzies', 'url': '/YP-admin/admin/Fuzzy/fuzzy/'},
                          #]})
#                          {'title': '#Reviews', 'url': '#'}]})

    #m.append({'title': 'Statistics',
              #'submenu': [{'title': 'Monthly', 'url': reverse('report-month')},
                          #{'title': 'Accounts', 'url': reverse('report-graph-users')},
                          #{'title': 'Login activity', 'url': reverse('report-graph-logins')},
                          #{'title': 'Usage', 'url': reverse('report-graph-usage')},
                          #{'title': 'Usage Stat', 'url': reverse('report-usage-stat')},
                          ##{'title': 'Usage Stat', 'url': '/YP-admin/admin/UsageStat/'},
                          #{'title': 'Content', 'url': reverse('report-graph-content')},
                          #{'title': 'Authoring', 'url': reverse('report-graph-auth')},
                          #{'title': 'Dynamic calibration', 'url': reverse('report-dynamic-calibration')},
                          #{'title': 'School teachers', 'url': reverse('report-graph-school-teachers')},
                          #{'title': 'Teacher removal log', 'url': reverse('school-unassign-teacher-log')},
                          #{'title': 'Mentoring students', 'url': reverse('report-graph-mentoring-students')},
                          #{'title': 'Search log', 'url': reverse('admin-search-log')},
                          #{'title': 'Quiz load times', 'url': reverse('report-graph-quiz')},
                          #{'title': 'Quiz questions timeouts', 'url': reverse('report-graph-question-timeout')},
                          #{'title': 'Teacher assignments', 'url': reverse('report-graph-assign')},
                          #{'title': 'User interface', 'url': reverse('stat-user-interface')},
                          #{'title': 'Student avatar selection', 'url': '/YP-admin/students/avatar_selection/' },
                          #{'title': 'QA log', 'url': reverse('admin-qa-log')},
                          #{'title': 'Offline results log', 'url': reverse('admin-oa-log')},
                          #{'title': 'Student email parents', 'url': reverse('students-email-parents-chart')},
                          #{'title': 'Student report downloads', 'url': reverse('student-report-download-chart')},
                          #{'title': 'Topic clicks', 'url': reverse('topic-clicks')},
                          #{'title': 'Hidding of tags', 'url': reverse('quiz-analysis-hide-tags')},
                          #{'title': 'Adding of tags', 'url': reverse('quiz-analysis-add-tags')},
                          #{'title': 'Charts Hide/Add tags', 'url': reverse('quiz-analysis-activity-chart')},
                          ##{'title': 'Student email parents', 'url': 'YP-admin/admin/Assignment/studentemailparent/'},
                          ##{'title': 'Student achive statistics', 'url': reverse('student-arch-stat')},
                          ##{'title': 'Search log', 'url': '/YP-admin/admin/Search/searchquerylog/'},
                          ##     {'title': '#Django/RRDTool', 'url': '/teacher/admin/UsageStat/usagefunction/'}
                          #]})

    m.append({'title': 'System',
              'submenu': [#{'title': 'Settings'},
                          #{'title': 'Runtime settings', 'url': '/YP-admin/admin/RuntimeSettings/runtimesettings/'},
                          #{'title': 'Promo messages', 'url': '/YP-admin/admin/PromoMessage/promomessage/'},
##                         {'title': '#Errors List', 'url': '#'},
                          #{'title': 'Cron tasks', 'url': '/YP-admin/admin/Cron/crontask/'},
                          {'title': 'Data updating log', 'url': '/gpsfun-admin/data_updating_log/'},
                          {'title': 'Last updating', 'url': '/gpsfun-admin/last_updates/'},
                          #{'title': 'Mail Batches', 'url': '/YP-admin/admin/main/mailbatch/'},
                          ## {'title': 'Batched Emails', 'url': '/YP-admin/admin/main/batchedemail/'}, no need for this
                          #{'title': 'Help Videos', 'url': '/YP-admin/admin/System/systemhelpvideo/'},
                          #{'title': 'Resource Usage', 'url': '/YP-admin/admin/ResourceUsage/'},
                          #{'title': 'Db Patches', 'url': '/YP-admin/admin/DbPatches/lastapplieddbpatch/'},
                         ]})


    m.append({'title': 'Logout', 'url': '/gpsfun-admin/logout/'})

    return dict(menu=m)
