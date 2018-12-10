from django.test import TestCase
from django.urls import reverse

from wagtail.core.models import Page


class APIViewTestMixin:

    url_namespace = 'wagtailmenus_api:v1'
    url_name = ''

    def get_base_url(self):
        if not self.url_name:
            raise NotImplementedError
        return reverse(self.url_namespace + ':' + self.url_name)

    def get(self, **kwargs):
        return self.client.get(self.get_base_url(), data=kwargs)


class TestMenuGeneratorIndexView(APIViewTestMixin, TestCase):

    url_name = 'index'
    fixtures = ['test.json']

    def test_loads_without_errors(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)


class TestMainMenuGeneratorView(APIViewTestMixin, TestCase):

    url_name = 'main_menu'
    fixtures = ['test.json']

    def test_loads_without_errors(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)


class TestFlatMenuGeneratorView(APIViewTestMixin, TestCase):

    url_name = 'flat_menu'
    fixtures = ['test.json']

    def test_loads_without_errors(self):
        response = self.get(handle='contact')
        self.assertEqual(response.status_code, 200)


class TestChildrenMenuGeneratorView(APIViewTestMixin, TestCase):

    url_name = 'children_menu'
    fixtures = ['test.json']

    def test_loads_without_errors(self):
        response = self.get(parent_page=Page.objects.get(url_path='/home/').id)
        self.assertEqual(response.status_code, 200)


class TestSectionMenuGeneratorView(APIViewTestMixin, TestCase):

    url_name = 'section_menu'
    fixtures = ['test.json']

    def test_loads_without_errors(self):
        response = self.get(section_root_page=Page.objects.get(url_path='/home/about-us/').id)
        self.assertEqual(response.status_code, 200)
