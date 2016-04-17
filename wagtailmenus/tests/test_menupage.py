from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils


class TestIndexView(TestCase, WagtailTestUtils):
    fixtures = ['test.json']

    def setUp(self):
        self.login()

    def get(self, **params):
        return self.client.get('/', params)

    def test_simple(self):
        response = self.get()

        self.assertEqual(response.status_code, 200)
