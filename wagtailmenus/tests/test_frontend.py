from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase
from wagtail.tests.utils import WagtailTestUtils


class TestMenuRendering(TestCase, WagtailTestUtils):
    fixtures = ['test.json']

    def test_homepage(self):
        """
        Test that homepage (based on `MenuPage`) renders without errors.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_about_us(self):
        """
        Test that 'About us' page (based on `MenuPage`), with 
        `repeat_in_subnav=True`, renders without errors.
        """
        response = self.client.get('/about-us/')
        self.assertEqual(response.status_code, 200)

    def test_meet_the_team(self):
        """
        Test that 'Meet the team' page (based on `Page`), and within a
        section with subnav, renders without errors.
        """
        response = self.client.get('/about-us/meet-the-team/')
        self.assertEqual(response.status_code, 200)

    def test_staff_vacancies(self):
        """
        Test that 'Staff vacancies' page (based on `Page`), with 
        `show_in_menus=False`, and within a section with subnav, renders
        without errors.
        """
        response = self.client.get('/about-us/staff-vacancies/')
        self.assertEqual(response.status_code, 200)

    def test_news_and_events(self):
        """
        Test that 'News and events' page (based on `MenuPage`), with 
        `repeat_in_subnav=False`, and within a section with subnav, renders
        without errors.
        """
        response = self.client.get('/news-and-events/')
        self.assertEqual(response.status_code, 200)

    def test_non_page(self):
        """
        Test that there are no errors when rendering page template without
        the `wagtailmenus.wagtail_hooks.wagtailmenu_params_helper()` method
        having run to add helpful bits to the context.
        """
        response = self.client.get('/custom-url/')
        self.assertEqual(response.status_code, 200)

    def test_main_menu_output_home(self):
        """
        Test that the HTML output by the 'main_menu' tag on the homepage
        renders as expected.
        """
        response = self.client.get('/')
        # Add assertions to compare rendered HTML against expected HTML 

    def test_main_menu_output_depth_3(self):
        """
        Test that the HTML output by the 'main_menu' tag on the 'About us'
        renders as expected.
        """
        response = self.client.get('/about-us/')
        # Add assertions to compare rendered HTML against expected HTML 

    def test_main_menu_output_depth_4(self):
        """
        Test that the HTML output by the 'main_menu' tag on the 'Meet the team'
        page renders as expected.
        """
        response = self.client.get('/about-us/meet-the-team/')
        # Add assertions to compare rendered HTML against expected HTML 

    def test_section_menu_output_depth_3(self):
        """
        Test that the HTML output by the 'section_menu' tag on the 'About us'
        page renders as expected.
        """
        response = self.client.get('/about-us/')
        # Add assertions to compare rendered HTML against expected HTML 

    def test_section_menu_output_depth_4(self):
        """
        Test that the HTML output by the 'section_menu' tag on the
        'Meet the team' page renders as expected.
        """
        response = self.client.get('/about-us/meet-the-team/')
        # Add assertions to compare rendered HTML against expected HTML 

    def test_cta_menu_output(self):
        """
        Test that the HTML output by the 'flat_menu' tag (when using the handle 
        'contact') renders as expected.
        """
        response = self.client.get('/')
        # Add assertions to compare rendered HTML against expected HTML 

    def test_footer_menu_output(self):
        """
        Test that the HTML output by the 'flat_menu' tag (when using the handle 
        'footer') renders as expected.
        """
        response = self.client.get('/')
        # Add assertions to compare rendered HTML against expected HTML 
