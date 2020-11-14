#!/usr/bin/env python
# -*- coding: utf-8 -*-

class IndexPageTopic(object):
    def __init__(self, title=None, language=None,
                 link=None, titles=None):
        """ You can specify title, title with language, or internationalized
        titles array/dict. Examples:

        topic = IndexPageTopic('MyTopic')
        or
        topic = IndexPageTopic('MyTopic', 'en')
        or
        topic = IndexPageTopic(titles={'en': 'MyTopic', 'ru': 'Тема'})
        """

        self._titles[language] = title
        self._link = link
        if titles_i18n:
            self._titles = dict(titles_i18n)

    @property
    def title(self, language=None):
        return self._titles[language]

    def _set_link(self, link):
        self._link = link

    def get_link(self, link):
        return self._link

    link = property(_set_link, get_link)


class IndexPage(object):
    index_template = None
    self_columns = []

    def __init__(self, name=None, app_name='admin'):
        self._topics = {}


    def add_topic(self, column, title):
        pass
