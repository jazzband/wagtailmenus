from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase
from bs4 import BeautifulSoup


class TestMenuRendering(TestCase):
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
        Test that the HTML output by the 'main_menu' tag on the homepage renders as expected.
        """
        response = self.client.get('/')
        # Add assertions to compare rendered HTML against expected HTML
        expected_menu_html = """<div class="collapse navbar-collapse navbar" id="main_menu_output"><ul class="nav navbar-nav"><li class="active"><a href="/">Home</a></li><li class=" dropdown"><a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" data-hover="dropdown" data-delay="400" data-close-others="true" aria-haspopup="true" aria-expanded="false">About</a><ul class="dropdown-menu" aria-labelledby="ddtoggle_6"><li class=""><a href="/about-us/">Section home</a></li><li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li><li class=""><a href="/about-us/our-heritage/">Our heritage</a></li><li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li></ul></li><li class=" dropdown"><a href="/news-and-events/" class="dropdown-toggle" id="ddtoggle_14" data-toggle="dropdown" data-hover="dropdown" data-delay="400" data-close-others="true" aria-haspopup="true" aria-expanded="false">News &amp; events</a><ul class="dropdown-menu" aria-labelledby="ddtoggle_14"><li class=""><a href="/news-and-events/latest-news/">Latest news</a></li><li class=""><a href="/news-and-events/upcoming-events/">Upcoming events</a></li><li class=""><a href="/news-and-events/press/">In the press</a></li></ul></li><li class=""><a href="http://google.co.uk">Google</a></li><li class=""><a href="/contact-us/">Contact us</a></li></ul></div>"""
        soup = BeautifulSoup(response.content, 'html5lib')
        menu_html = soup.find(id='main_menu_output').decode()
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_main_menu_output_about_us(self):
        """
        Test that the HTML output by the 'main_menu' tag on the 'About us' page renders as expected.
        """
        response = self.client.get('/about-us/')
        # Add assertions to compare rendered HTML against expected HTML
        expected_menu_html = """<div class="collapse navbar-collapse navbar" id="main_menu_output"><ul class="nav navbar-nav"><li class=""><a href="/">Home</a></li><li class="ancestor dropdown"><a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" data-hover="dropdown" data-delay="400" data-close-others="true" aria-haspopup="true" aria-expanded="false">About</a><ul class="dropdown-menu" aria-labelledby="ddtoggle_6"><li class="active"><a href="/about-us/">Section home</a></li><li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li><li class=""><a href="/about-us/our-heritage/">Our heritage</a></li><li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li></ul></li><li class=" dropdown"><a href="/news-and-events/" class="dropdown-toggle" id="ddtoggle_14" data-toggle="dropdown" data-hover="dropdown" data-delay="400" data-close-others="true" aria-haspopup="true" aria-expanded="false">News &amp; events</a><ul class="dropdown-menu" aria-labelledby="ddtoggle_14"><li class=""><a href="/news-and-events/latest-news/">Latest news</a></li><li class=""><a href="/news-and-events/upcoming-events/">Upcoming events</a></li><li class=""><a href="/news-and-events/press/">In the press</a></li></ul></li><li class=""><a href="http://google.co.uk">Google</a></li><li class=""><a href="/contact-us/">Contact us</a></li></ul></div>"""
        soup = BeautifulSoup(response.content, 'html5lib')
        menu_html = soup.find(id='main_menu_output').decode()
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_main_menu_output_meet_the_team(self):
        """
        Test that the HTML output by the 'main_menu' tag on the 'Meet the team' page renders as expected.
        """
        response = self.client.get('/about-us/meet-the-team/')
        # Add assertions to compare rendered HTML against expected HTML
        expected_menu_html = """<div class="collapse navbar-collapse navbar" id="main_menu_output"><ul class="nav navbar-nav"><li class=""><a href="/">Home</a></li><li class="ancestor dropdown"><a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" data-hover="dropdown" data-delay="400" data-close-others="true" aria-haspopup="true" aria-expanded="false">About</a><ul class="dropdown-menu" aria-labelledby="ddtoggle_6"><li class=""><a href="/about-us/">Section home</a></li><li class="active"><a href="/about-us/meet-the-team/">Meet the team</a></li><li class=""><a href="/about-us/our-heritage/">Our heritage</a></li><li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li></ul></li><li class=" dropdown"><a href="/news-and-events/" class="dropdown-toggle" id="ddtoggle_14" data-toggle="dropdown" data-hover="dropdown" data-delay="400" data-close-others="true" aria-haspopup="true" aria-expanded="false">News &amp; events</a><ul class="dropdown-menu" aria-labelledby="ddtoggle_14"><li class=""><a href="/news-and-events/latest-news/">Latest news</a></li><li class=""><a href="/news-and-events/upcoming-events/">Upcoming events</a></li><li class=""><a href="/news-and-events/press/">In the press</a></li></ul></li><li class=""><a href="http://google.co.uk">Google</a></li><li class=""><a href="/contact-us/">Contact us</a></li></ul></div>"""
        soup = BeautifulSoup(response.content, 'html5lib')
        menu_html = soup.find(id='main_menu_output').decode()
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_section_menu_output_about_us(self):
        """
        Test that the HTML output by the 'section_menu' tag on the 'About us' page renders as expected.
        """
        response = self.client.get('/about-us/')
        # Add assertions to compare rendered HTML against expected HTML
        expected_menu_html = """<div id="nav-section"><nav class="nav-section" role="navigation"><a href="/about-us/" class="ancestor section_root">About us</a><ul><li class="active"><a href="/about-us/">Section home</a></li><li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li><li class=""><a href="/about-us/our-heritage/">Our heritage</a></li><li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li></ul></nav></div>"""
        soup = BeautifulSoup(response.content, 'html5lib')
        menu_html = soup.find(id='nav-section').decode()
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_section_menu_output_meet_the_team(self):
        """
        Test that the HTML output by the 'section_menu' tag on the 'Meet the team' page renders as expected.
        """
        response = self.client.get('/about-us/meet-the-team/')
        # Add assertions to compare rendered HTML against expected HTML
        expected_menu_html = """<div id="nav-section"><nav class="nav-section" role="navigation"><a href="/about-us/" class="ancestor section_root">About us</a><ul><li class=""><a href="/about-us/">Section home</a></li><li class="active"><a href="/about-us/meet-the-team/">Meet the team</a></li><li class=""><a href="/about-us/our-heritage/">Our heritage</a></li><li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li></ul></nav></div>"""
        soup = BeautifulSoup(response.content, 'html5lib')
        menu_html = soup.find(id='nav-section').decode()
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_contact_flat_menu_output(self):
        """
        Test that the HTML output by the 'flat_menu' tag (when using the handle 'contact') renders as expected.
        """
        response = self.client.get('/')
        # Add assertions to compare rendered HTML against expected HTML
        expected_menu_html = """<div id="nav-contact"><div class="flat-menu contact no_heading"><ul><li class=""><a href="/contact-us/#offices">Call us</a></li><li class=""><a href="#advisor-chat">Chat to an advisor</a></li><li class=""><a href="#request-callback">Request a callback</a></li></ul></div></div>"""
        soup = BeautifulSoup(response.content, 'html5lib')
        menu_html = soup.find(id='nav-contact').decode()
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_footer_flat_menu_output(self):
        """
        Test that the HTML output by the 'flat_menu' tag (when using the handle 'footer') renders as expected.
        """
        response = self.client.get('/')
        # Add assertions to compare rendered HTML against expected HTML
        expected_menu_html = """<div id="nav-footer"><div class="flat-menu footer with_heading"><h4>Important links</h4><ul><li class=""><a href="/legal/accessibility/">Accessibility</a></li><li class=""><a href="/legal/privacy-policy/">Privacy policy</a></li><li class=""><a href="/legal/terms-and-conditions/">Terms and conditions</a></li></ul></div></div>"""
        soup = BeautifulSoup(response.content, 'html5lib')
        menu_html = soup.find(id='nav-footer').decode()
        self.assertHTMLEqual(menu_html, expected_menu_html)
