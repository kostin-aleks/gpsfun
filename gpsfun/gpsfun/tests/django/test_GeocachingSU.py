#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import json
from datetime import date
from django.test.client import Client
from django.urls import reverse


class GeocachingTest(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.year = date.today().year
        self.previous_year = self.year - 1

    def test_home_page(self):
        response = self.client.get(reverse('geocaching-su'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('GEOCACHING.SU. Statistics' in response.content)

    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('On this site you will find information related to entertainment which is called' in response.content)

    def test_cache_by_index(self):
        response = self.client.get(reverse('cach-rate-by-index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Rating caches on the integrated index' in response.content)

    def test_cache_by_found(self):
        response = self.client.get(reverse('cach-rate-by-found'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Rating caches on the number of entries in a logbook' in response.content)

    def test_cache_by_recommend(self):
        response = self.client.get(reverse('cach-rate-by-recommend'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Rating caches on the number of recommendations' in response.content)

    def test_caches_stat(self):
        response = self.client.get(reverse('geocaching-su-cach-stat'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Count of caches over the years' in response.content)
        self.assertTrue('Count of caches per years per type' in response.content)

    def test_geocachers_activity(self):
        response = self.client.get(reverse('geocacher-activity'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Activities of geocachers by the years, light color for visits and dark color for creating' in response.content)
        self.assertTrue('Creating of caches by the years, light color for traditional, dark color for virtual caches' in response.content)

    def test_geocachers_countries(self):
        response = self.client.get(reverse('geocaching-su-geocacher-stat-countries'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Russia' in response.content)
        self.assertTrue('Ukraine' in response.content)

    def test_geocachers_rate(self):
        response = self.client.get(reverse('geocacher-rate'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Geocachers activity' in response.content)

    def test_geocachers_rate_all(self):
        response = self.client.get(reverse('geocacher-rate'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Geocachers activity' in response.content)
        self.assertTrue('All caches' in response.content)

    def test_geocachers_rate_unreal(self):
        response = self.client.get(reverse('geocacher-rate-vi'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Geocachers activity' in response.content)
        self.assertTrue('Unreal caches' in response.content)

    def test_geocachers_rate_real(self):
        response = self.client.get(reverse('geocacher-rate-tr'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Geocachers activity' in response.content)
        self.assertTrue('Real caches' in response.content)

    def test_geocachers_rate_all_current(self):
        response = self.client.get(reverse('geocacher-rate-all-curr'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Geocachers activity' in response.content)
        self.assertTrue('%s. All caches'%self.year in response.content)

    def test_geocachers_rate_unreal_current(self):
        response = self.client.get(reverse('geocacher-rate-vi-curr'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Geocachers activity' in response.content)
        self.assertTrue('%s. Unreal caches'%self.year in response.content)

    def test_geocachers_rate_real_current(self):
        response = self.client.get(reverse('geocacher-rate-tr-curr'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Geocachers activity' in response.content)
        self.assertTrue('%s. Real caches'%self.year in response.content)

    def test_geocachers_rate_all_last(self):
        response = self.client.get(reverse('geocacher-rate-all-last'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Geocachers activity' in response.content)
        self.assertTrue('%s. All caches'%self.previous_year in response.content)

    def test_geocachers_rate_unreal_last(self):
        response = self.client.get(reverse('geocacher-rate-vi-last'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Geocachers activity' in response.content)
        self.assertTrue('%s. Unreal caches'%self.previous_year in response.content)

    def test_geocachers_rate_real_last(self):
        response = self.client.get(reverse('geocacher-rate-tr-last'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Geocachers activity' in response.content)
        self.assertTrue('%s. Real caches'%self.previous_year in response.content)

    def test_converter(self):
        post_data = {'input': '-45.77777'}
        kwargs = {'HTTP_X_REQUESTED_WITH':'XMLHttpRequest'}
        response = self.client.post(reverse('ajax-converter'), post_data,  **kwargs)
        r = json.loads(response.content)

        self.assertTrue(r['status']=='OK')
        self.assertTrue(r['dm']==u"45\xb0 46.666'")
        self.assertTrue(r['dms']==u'45\xb0 46\' 39.97"')
        self.assertTrue(r['d']=="45.777770")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
