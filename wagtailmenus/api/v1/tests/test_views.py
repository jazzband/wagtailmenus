from django.test import TestCase
from django.urls import reverse

from wagtail.core.models import Page


class MenuGeneratorViewTestMixin:

    base_url_name = ''

    def get_base_url(self):
        if not self.base_url_name:
            raise NotImplementedError
        return reverse(self.base_url_name)

    def get(self, **kwargs):
        return self.client.get(self.get_base_url(), data=kwargs)


class TestMainMenuGeneratorView(MenuGeneratorViewTestMixin, TestCase):

    base_url_name = 'wagtailmenus_api:v1:main_menu'
    fixtures = ['test.json']

    def test_loads_without_errors(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)


class TestFlatMenuGeneratorView(MenuGeneratorViewTestMixin, TestCase):

    base_url_name = 'wagtailmenus_api:v1:flat_menu'
    fixtures = ['test.json']

    def test_loads_without_errors(self):
        response = self.get(handle='contact')
        self.assertEqual(response.status_code, 200)


class TestChildrenMenuGeneratorView(MenuGeneratorViewTestMixin, TestCase):

    base_url_name = 'wagtailmenus_api:v1:children_menu'
    fixtures = ['test.json']

    def test_loads_without_errors(self):
        response = self.get(parent_page=Page.objects.get(url_path='/home/').id)
        self.assertEqual(response.status_code, 200)


class TestSectionMenuGeneratorView(MenuGeneratorViewTestMixin, TestCase):

    base_url_name = 'wagtailmenus_api:v1:section_menu'
    fixtures = ['test.json']

    def test_loads_without_errors(self):
        response = self.get(section_root_page=Page.objects.get(url_path='/home/about-us/').id)
        self.assertEqual(response.status_code, 200)
