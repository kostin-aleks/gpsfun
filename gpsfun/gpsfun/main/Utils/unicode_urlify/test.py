# -*- coding: utf-8 -*-

import unittest
from urlify import urlify

class PinYinTestCase(unittest.TestCase):

    def testEnglish(self):
        self.assertEqual(urlify(u'WOW. We Say ENGLISH.'),
                         u'wow-we-say-english')

    def testWestern(self):
        self.assertEqual(urlify(u'ÀÞβ Λğ-Ґє'),
                         u'athb-lg-gye')

    def testEmpty(self):
        self.assertEqual(urlify(u''),
                          u'default')

    def testStopWords(self):
        self.assertEqual(urlify(u'hello, this is an blahblah'),
                         u'hello-blahblah')

    def testReservedWords(self):
        self.assertEqual(urlify(u'  blog  '),
                         u'default')

    def testMaxLengthLimit(self):
        self.assertEqual(urlify(u'urlstring url instance class request embodies. Example, data headers, calling:'),
                         u'urlstring-url-instance-class-request-embodies-exam')

    # additional tests
    def testRus(self):
        self.assertEqual(urlify(u'русский текст'),
                         u'russkij-tekst')

    def testArabic(self):
        # NOTE: arabic not supported: recognize only space in center;
        # therefore return ''

        r = urlify(u'اللغة العربية')
        self.assertEqual(r, '')

    def testChines(self):
        # NOTE: no one character in line suppoerted; return 'default'
        r = urlify(u'漢語')
        self.assertEqual(r, 'default')


if __name__ == '__main__':
    unittest.main()
