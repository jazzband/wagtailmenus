from django.test import TestCase
from wagtail.core.models import Page, Site

from wagtailmenus import get_main_menu_model
from .mixins import APIViewTestMixin


class TestMenuGeneratorIndexView(APIViewTestMixin, TestCase):

    url_name = 'index'
    fixtures = ['test.json']

    def test_loads_without_errors(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)


class TestMainMenuGeneratorView(APIViewTestMixin, TestCase):

    url_name = 'main_menu'
    fixtures = ['test.json']

    def setUp(self):
        self.query_params = {
            'current_url': 'https://www.wagtailmenus.co.uk/about-us/',
            'format': 'json',
            'apply_active_classes': 'true',
            'allow_repeating_parents': 'true',
            'use_relative_page_urls': 'true',
        }

    def test_renders_json_data_by_default(self):
        response = self.get(**self.query_params)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

    def test_custom_renderer_renders_argument_form_to_template(self):
        with self.assertTemplateUsed('wagtailmenus/api/argument_form_modal.html'):
            self.query_params['format'] = 'api'
            response = self.get(**self.query_params)
            self.assertEqual(response.status_code, 200)

    def test_responds_with_200_if_no_such_menu_exists_but_one_is_created(self):
        model = get_main_menu_model()
        new_site = Site.objects.create(hostname='new.com', root_page_id=1)
        self.assertFalse(model.objects.filter(site_id=new_site.id).exists())

        self.query_params['current_url'] = 'http://new.com/'
        response = self.get(**self.query_params)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(model.objects.filter(site_id=new_site.id).count())


class TestFlatMenuGeneratorView(APIViewTestMixin, TestCase):

    url_name = 'flat_menu'
    fixtures = ['test.json']

    def setUp(self):
        self.query_params = {
            'handle': 'contact',
            'current_url': 'https://www.wagtailmenus.co.uk/about-us/',
            'format': 'json',
            'apply_active_classes': 'true',
            'allow_repeating_parents': 'true',
            'use_relative_page_urls': 'true',
        }

    def test_renders_json_data_by_default(self):
        response = self.get(**self.query_params)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

    def test_custom_renderer_renders_argument_form_to_template(self):
        with self.assertTemplateUsed('wagtailmenus/api/argument_form_modal.html'):
            self.query_params['format'] = 'api'
            response = self.get(**self.query_params)
            self.assertEqual(response.status_code, 200)

    def test_responds_with_400_if_non_slug_handle_provided(self):
        self.query_params['handle'] = 'blah!blah!blah!'
        response = self.get(**self.query_params)
        self.assertEqual(response.status_code, 400)
        json = response.json()
        self.assertIn('handle', json)
        self.assertEqual(
            json['handle'][0],
            "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens."
        )


class TestChildrenMenuGeneratorView(APIViewTestMixin, TestCase):

    url_name = 'children_menu'
    fixtures = ['test.json']

    def setUp(self):
        self.parent_page = Page.objects.get(url_path='/home/')
        self.query_params = {
            'parent_page_id': self.parent_page.pk,
            'current_url': 'https://www.wagtailmenus.co.uk/about-us/',
            'format': 'json',
            'apply_active_classes': 'true',
            'allow_repeating_parents': 'true',
            'use_relative_page_urls': 'true',
        }

    def test_renders_json_data_by_default(self):
        response = self.get(**self.query_params)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

    def test_custom_renderer_renders_argument_form_to_template(self):
        with self.assertTemplateUsed('wagtailmenus/api/argument_form_modal.html'):
            self.query_params['format'] = 'api'
            response = self.get(**self.query_params)
            self.assertEqual(response.status_code, 200)


class TestSectionMenuGeneratorView(APIViewTestMixin, TestCase):

    url_name = 'section_menu'
    fixtures = ['test.json']

    def setUp(self):
        self.section_root_page = Page.objects.get(url_path='/home/about-us/')
        self.query_params = {
            'section_root_page_id': self.section_root_page.pk,
            'current_url': 'https://www.wagtailmenus.co.uk/about-us/',
            'format': 'json',
            'apply_active_classes': 'true',
            'allow_repeating_parents': 'true',
            'use_relative_page_urls': 'true',
        }

    def test_renders_json_data_by_default(self):
        response = self.get(**self.query_params)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

    def test_custom_renderer_renders_argument_form_to_template(self):
        with self.assertTemplateUsed('wagtailmenus/api/argument_form_modal.html'):
            self.query_params['format'] = 'api'
            response = self.get(**self.query_params)
            self.assertEqual(response.status_code, 200)
