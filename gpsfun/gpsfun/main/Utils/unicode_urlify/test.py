"""
test
"""

import unittest
from .urlify import urlify


class PinYinTestCase(unittest.TestCase):
    """
    PinYinTestCase
    """

    def test_english(self):
        """ test English """
        self.assertEqual(urlify('WOW. We Say ENGLISH.'), 'wow-we-say-english')

    def test_western(self):
        """ test Western """
        self.assertEqual(urlify('ÀÞβ Λğ-Ґє'), 'athb-lg-gye')

    def test_empty(self):
        """ test Empty """
        self.assertEqual(urlify(''), 'default')

    def test_stop_words(self):
        """ test Stop Words """
        self.assertEqual(urlify('hello, this is an blahblah'),
                         'hello-blahblah')

    def test_reserved_words(self):
        """ test Reserved Words """
        self.assertEqual(urlify('  blog  '), 'default')

    def test_max_length_limit(self):
        """ test Max Length Limit """
        self.assertEqual(urlify('urlstring url instance class request embodies. Example, data headers, calling:'),
                         'urlstring-url-instance-class-request-embodies-exam')

    # additional tests
    def test_rus(self):
        """ test Rus """
        self.assertEqual(urlify('русский текст'), 'russkij-tekst')

    def test_arabic(self):
        """ test Arabic """
        # NOTE: arabic not supported: recognize only space in center;
        # therefore return ''

        result = urlify('اللغة العربية')
        self.assertEqual(result, '')

    def test_chines(self):
        """ test Chines """
        # NOTE: no one character in line suppoerted; return 'default'
        result = urlify('漢語')
        self.assertEqual(result, 'default')


if __name__ == '__main__':
    unittest.main()
