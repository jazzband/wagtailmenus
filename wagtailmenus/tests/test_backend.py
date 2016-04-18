from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils


class TestMainMenuList(TestCase, WagtailTestUtils):
    fixtures = ['test.json']

    def setUp(self):
        self.login()


class TestMainMenuEdit(TestCase, WagtailTestUtils):
    fixtures = ['test.json']

    def setUp(self):
        self.login()


class TestFlatMenuList(TestCase, WagtailTestUtils):
    fixtures = ['test.json']

    def setUp(self):
        self.login()


class TestFlatMenuEdit(TestCase, WagtailTestUtils):
    fixtures = ['test.json']

    def setUp(self):
        self.login()
