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

    def test_loads_without_errors(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)

    def test_responds_with_200_if_no_such_menu_exists_because_one_is_created(self):
        model = get_main_menu_model()
        new_site = Site.objects.create(hostname='new.com', root_page_id=1)
        self.assertFalse(model.objects.filter(site_id=new_site.id).exists())
        response = self.get(site=new_site.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(model.objects.filter(site_id=new_site.id).count())


class TestFlatMenuGeneratorView(APIViewTestMixin, TestCase):

    url_name = 'flat_menu'
    fixtures = ['test.json']

    def test_renders_json_data_by_default(self):
        response = self.get(handle='contact')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

    def test_custom_renderer_renders_argument_form_to_template(self):
        with self.assertTemplateUsed('wagtailmenus/api/argument_form_modal.html'):
            response = self.get(handle='contact', format='api')
            self.assertEqual(response.status_code, 200)

    def test_responds_with_404_if_no_such_menu_exists(self):
        response = self.get(site=1, handle='blahblahblah')
        self.assertEqual(response.status_code, 404)

    def test_responds_with_400_if_non_slug_handle_provided(self):
        response = self.get(site=1, handle='blah!blah!blah!')
        self.assertEqual(response.status_code, 400)
        json = response.json()
        self.assertIn('handle', json)
        self.assertEqual(json['handle'][0], "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.")


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
