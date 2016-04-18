from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils


class TestIndexView(TestCase, WagtailTestUtils):
    fixtures = ['test.json']

    def setUp(self):
        self.login()

    def test_main_menu_output(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/about-us/')
        self.assertEqual(response.status_code, 200)

    def test_section_menu_output(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/about-us/')
        self.assertEqual(response.status_code, 200)

    def test_cta_menu_output(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_footer_menu_output(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
