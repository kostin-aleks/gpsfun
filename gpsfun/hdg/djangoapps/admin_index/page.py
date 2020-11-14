#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Topic(object):
    def __init__(self, title=None, link=None,
                 lang=None,
                 titles=None):
        """ You can specify title, title with language, or internationalized
        titles array/dict. Examples:

        >>> topic = Topic('MyTopic')
        >>> topic1 = Topic('MyTopic', lang='en', link='/lnk')
        >>> assert topic1.get_title()==None
        >>> topic1.get_title('en')
        'MyTopic'

        >>> topic2 = Topic(titles={'en': 'MyTopic', 'ru': 'RuTopic'})
        >>> topic2.get_title('ru')
        'RuTopic'
        >>> topic2.get_title('en')
        'MyTopic'
        >>> topic2.get_title()
        >>>


        >>> topic3 = Topic(titles={'en': 'MyTopic', 'ru': 'ttt'}, link='/')
        >>> assert topic3.link == '/'
        >>> topic3.link = '/xxx/'
        >>> topic3.link
        '/xxx/'


        """
        self._titles = {}
        self._titles[lang] = title
        if titles:
            self._titles = dict(titles)
        self.link = link

    def get_title(self, language=None):
        return self._titles.get(language, None)

    def __unicode__(self):
        return self._titles.get(None, None)


class Column(object):
    def __init__(self, title, topic=None):
        self._title = title
        self._topics = []
        if topic:
            self.add_topic(topic)

    def add_topic(self, topic):
        self._topics.append(topic)

    @property
    def title(self):
        return self._title

    def __unicode__(self):
        """
        >>> c = Column('tst')
        >>> unicode(c)==u'tst'
        True
        """
        return self._title

    @property
    def topics(self):
        """
        >>> c = Column('tst')
        >>> c.add_topic(Topic('zzz'))
        >>> [topic.get_title() for topic in c.topics]
        ['zzz']
        """
        return self._topics

    def subtopics(self):
        subtopics = []
        current_topic = {'topic': self._topics[0], 'topics': []}
        for t in self._topics[1:]:
            if not t.link:
                subtopics.append(current_topic)
                current_topic = {'topic': t, 'topics': []}
            else:
                current_topic['topics'].append(t)
        subtopics.append(current_topic)
        return subtopics


class Page(object):
    logo = '/manage/images/logo.png'
    css = 'manage/css/manage.css'

    def __init__(self, template_name='manage/index.html'):
        self._template = template_name
        self._columns = []
        self._info_registry = []

    def add_topic(self, column_title, topic):
        """
        >>> index=Page()
        >>> index.add_topic('col1', Topic('Pages', '/pages'))
        """
        for column in self._columns:
            if unicode(column) == column_title:
                column.add_topic(topic)
                break
        else:
            self._columns.append(Column(column_title, topic))

    def columns(self):
        """
        >>> index=Page()
        >>> index.add_topic('col1', Topic('Pages', '/pages'))
        >>> [c.title for c in index.columns()]
        ['col1']
        >>>
        """
        return self._columns

    def add_info(self, funcref):
        """ add information to information block """
        self._info_registry.append(funcref)

    def info(self):
        """
        >>> mypage = Page()
        >>> def myfunc(lang=None):
        ... 	return [('1','2')]
        ...
        >>> mypage.add_info(myfunc)
        >>> [d for d in mypage.info()]
        [('1', '2')]
        """
        for func in self._info_registry:
            res = func()
            for r in res:
                yield r

if __name__ == "__main__":
    import doctest
    doctest.testmod()
