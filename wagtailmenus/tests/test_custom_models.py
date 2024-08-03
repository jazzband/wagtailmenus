# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from wagtailmenus import get_flat_menu_model, get_main_menu_model
from wagtailmenus.models import FlatMenu, MainMenu
from wagtailmenus.tests.models import (CustomFlatMenu, CustomFlatMenuItem,
                                       CustomMainMenu, CustomMainMenuItem,
                                       FlatMenuCustomMenuItem,
                                       MainMenuCustomMenuItem)


@override_settings(
    WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME='custom_menu_items',
    WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME='custom_menu_items',
    LANGUAGE_CODE="de",
)
class TestCustomMenuItemsGerman(TestCase):
    fixtures = ['test.json', 'test_custom_models.json']
    maxDiff = None

    def setUp(self):
        get_user_model().objects._create_user(
            username='test1', email='test1@email.com', password='password',
            is_staff=True, is_superuser=True)
        self.client.login(username='test1', password='password')

    def test_main_menu_models_correct(self):
        self.assertEqual(get_main_menu_model(), MainMenu)
        menu_obj = get_main_menu_model().objects.first()
        self.assertEqual(
            menu_obj.get_menu_items_manager().model,
            MainMenuCustomMenuItem
        )

    def test_flat_menu_models_correct(self):
        self.assertEqual(get_flat_menu_model(), FlatMenu)
        menu_obj = get_flat_menu_model().objects.first()
        self.assertEqual(
            menu_obj.get_menu_items_manager().model,
            FlatMenuCustomMenuItem
        )

    def test_mainmenu_list(self):
        response = self.client.get('/admin/wagtailmenus/mainmenu/')
        self.assertRedirects(response, '/admin/wagtailmenus/mainmenu/edit/1/')

    def test_mainmenu_edit(self):
        response = self.client.get(
            '/admin/wagtailmenus/mainmenu/edit/1/')
        # Test 'get_error_message' method on view for additional coverage
        view = response.context['view']
        self.assertTrue(view.get_error_message())

    def test_flatmenu_list(self):
        response = self.client.get('/admin/wagtailmenus/flatmenu/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<th scope="col"  class="sortable column-site">')
        self.assertNotContains(response, '<div class="changelist-filter col3">')

    def test_flatmenu_edit(self):
        response = self.client.get(
            '/admin/wagtailmenus/flatmenu/edit/1/')
        self.assertEqual(response.status_code, 200)

    def test_translated_main_menu(self):
        response = self.client.get('/superheroes/dc-comics/batman/')
        soup = BeautifulSoup(response.content, 'html.parser')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='main-menu-two-levels').decode()
        expected_menu_html = """
        <div id="main-menu-two-levels">
            <ul class="nav navbar-nav">
                <li class=""><a href="/">Home</a></li>
                <li class=" dropdown">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Etwa <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class=""><a href="/about-us/">Abschnitt zu Hause</a></li>
                        <li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" dropdown">
                    <a href="/news-and-events/" class="dropdown-toggle" id="ddtoggle_14" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">News &amp; Veranstaltungen <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_14">
                        <li class=""><a href="/news-and-events/latest-news/">Latest news</a></li>
                        <li class=""><a href="/news-and-events/upcoming-events/">Upcoming events</a></li>
                        <li class=""><a href="/news-and-events/press/">In the press</a></li>
                    </ul>
                </li>
                <li class=""><a href="http://google.co.uk">Google</a></li>
                <li class=" dropdown">
                    <a href="/contact-us/" class="dropdown-toggle" id="ddtoggle_18" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Contact us <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_18">
                        <li class="support"><a href="/contact-us/#support">Get support</a></li>
                        <li class="call"><a href="/contact-us/#call">Speak to someone</a></li>
                        <li class="map"><a href="/contact-us/#map">Map &amp; directions</a></li>
                    </ul>
                </li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_translated_contact_menu(self):
        """
        Test that the HTML output by the 'flat_menu' tag (when using the handle
        'contact') renders as expected.
        """
        response = self.client.get('/superheroes/dc-comics/batman/')
        soup = BeautifulSoup(response.content, 'html.parser')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='nav-contact').decode()
        expected_menu_html = """
        <div id="nav-contact">
            <div class="flat-menu contact no_heading">
                <ul>
                    <li class="">
                        <a href="/contact-us/#offices">Rufen Sie uns an</a>
                    </li>
                    <li class="">
                        <a href="#advisor-chat">Chat mit einem Berater</a>
                    </li>
                    <li class="">
                        <a href="#request-callback">Rückruf anfordern</a>
                    </li>
                </ul>
            </div>
        </div>"""
        self.assertHTMLEqual(menu_html, expected_menu_html)


@override_settings(
    WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME='custom_menu_items',
    WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME='custom_menu_items',
    LANGUAGE_CODE="fr",
)
class TestCustomMenuItemsFrench(TestCase):
    fixtures = ['test.json', 'test_custom_models.json']
    maxDiff = None

    def test_translated_main_menu(self):
        response = self.client.get('/superheroes/dc-comics/batman/')
        soup = BeautifulSoup(response.content, 'html.parser')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='main-menu-two-levels').decode()
        expected_menu_html = """
        <div id="main-menu-two-levels">
            <ul class="nav navbar-nav">
                <li class=""><a href="/">Home</a></li>
                <li class=" dropdown">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Sur <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class=""><a href="/about-us/">Section accueil</a></li>
                        <li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" dropdown">
                    <a href="/news-and-events/" class="dropdown-toggle" id="ddtoggle_14" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Nouvelles et événements <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_14">
                        <li class=""><a href="/news-and-events/latest-news/">Latest news</a></li>
                        <li class=""><a href="/news-and-events/upcoming-events/">Upcoming events</a></li>
                        <li class=""><a href="/news-and-events/press/">In the press</a></li>
                    </ul>
                </li>
                <li class=""><a href="http://google.co.uk">Google</a></li>
                <li class=" dropdown">
                    <a href="/contact-us/" class="dropdown-toggle" id="ddtoggle_18" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Contact us <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_18">
                        <li class="support"><a href="/contact-us/#support">Get support</a></li>
                        <li class="call"><a href="/contact-us/#call">Speak to someone</a></li>
                        <li class="map"><a href="/contact-us/#map">Map &amp; directions</a></li>
                    </ul>
                </li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_translated_menu_french(self):
        """
        Test that the HTML output by the 'flat_menu' tag (when using the
        handle 'contact') renders as expected.
        """
        response = self.client.get('/superheroes/dc-comics/batman/')
        soup = BeautifulSoup(response.content, 'html.parser')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='nav-contact').decode()
        expected_menu_html = """
        <div id="nav-contact">
            <div class="flat-menu contact no_heading">
                <ul>
                    <li class="">
                        <a href="/contact-us/#offices">Appelez-nous</a>
                    </li>
                    <li class="">
                        <a href="#advisor-chat">Chat à un conseiller</a>
                    </li>
                    <li class="">
                        <a href="#request-callback">Demander un rappel</a>
                    </li>
                </ul>
            </div>
        </div>"""
        self.assertHTMLEqual(menu_html, expected_menu_html)


@override_settings(
    WAGTAILMENUS_MAIN_MENU_MODEL='tests.CustomMainMenu',
    WAGTAILMENUS_FLAT_MENU_MODEL='tests.CustomFlatMenu',
    WAGTAILMENUS_SECTION_MENU_CLASS='wagtailmenus.tests.models.CustomSectionMenu',
)
class TestCustomMenuModels(TestCase):
    fixtures = ['test.json', 'test_custom_models.json']
    maxDiff = None

    def setUp(self):
        get_user_model().objects._create_user(
            username='test1', email='test1@email.com', password='password',
            is_staff=True, is_superuser=True)
        self.client.login(username='test1', password='password')

    def test_main_menu_models_correct(self):
        self.assertEqual(get_main_menu_model(), CustomMainMenu)
        menu_obj = get_main_menu_model().objects.first()
        self.assertEqual(
            menu_obj.get_menu_items_manager().model,
            CustomMainMenuItem
        )

    def test_flat_menu_models_correct(self):
        self.assertEqual(get_flat_menu_model(), CustomFlatMenu)
        menu_obj = get_flat_menu_model().objects.first()
        self.assertEqual(
            menu_obj.get_menu_items_manager().model,
            CustomFlatMenuItem
        )

    @override_settings(LANGUAGE_CODE="it",)
    def test_custom_main_menu_english(self):
        response = self.client.get('/superheroes/dc-comics/batman/')
        soup = BeautifulSoup(response.content, 'html.parser')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='main-menu-two-levels').decode()
        expected_menu_html = """
        <div id="main-menu-two-levels">
            <ul class="nav navbar-nav">
                <li class=""><a href="/">Home</a></li>
                <li class=" dropdown">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class=""><a href="/about-us/">Section home</a></li>
                        <li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" dropdown">
                    <a href="/news-and-events/" class="dropdown-toggle" id="ddtoggle_14" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">News &amp; events <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_14">
                        <li class=""><a href="/news-and-events/latest-news/">Latest news</a></li>
                        <li class=""><a href="/news-and-events/upcoming-events/">Upcoming events</a></li>
                        <li class=""><a href="/news-and-events/press/">In the press</a></li>
                    </ul>
                </li>
                <li class=""><a href="http://google.co.uk">Google</a></li>
                <li class=" dropdown">
                    <a href="/contact-us/" class="dropdown-toggle" id="ddtoggle_18" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Contact us <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_18">
                        <li class="support"><a href="/contact-us/#support">Get support</a></li>
                        <li class="call"><a href="/contact-us/#call">Speak to someone</a></li>
                        <li class="map"><a href="/contact-us/#map">Map &amp; directions</a></li>
                    </ul>
                </li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    @override_settings(LANGUAGE_CODE="de",)
    def test_custom_main_menu_german(self):
        response = self.client.get('/superheroes/dc-comics/batman/')
        soup = BeautifulSoup(response.content, 'html.parser')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='main-menu-two-levels').decode()
        expected_menu_html = """
        <div id="main-menu-two-levels">
            <ul class="nav navbar-nav">
                <li class=""><a href="/">Home</a></li>
                <li class=" dropdown">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Etwa <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class=""><a href="/about-us/">Abschnitt zu Hause</a></li>
                        <li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" dropdown">
                    <a href="/news-and-events/" class="dropdown-toggle" id="ddtoggle_14" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">News &amp; Veranstaltungen <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_14">
                        <li class=""><a href="/news-and-events/latest-news/">Latest news</a></li>
                        <li class=""><a href="/news-and-events/upcoming-events/">Upcoming events</a></li>
                        <li class=""><a href="/news-and-events/press/">In the press</a></li>
                    </ul>
                </li>
                <li class=""><a href="http://google.co.uk">Google</a></li>
                <li class=" dropdown">
                    <a href="/contact-us/" class="dropdown-toggle" id="ddtoggle_18" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Contact us <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_18">
                        <li class="support"><a href="/contact-us/#support">Get support</a></li>
                        <li class="call"><a href="/contact-us/#call">Speak to someone</a></li>
                        <li class="map"><a href="/contact-us/#map">Map &amp; directions</a></li>
                    </ul>
                </li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_custom_flat_menu_english(self):
        """
        Test that the HTML output by the 'flat_menu' tag (when using the handle
        'contact') renders as expected.
        """
        response = self.client.get('/superheroes/dc-comics/batman/')
        soup = BeautifulSoup(response.content, 'html.parser')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='nav-contact').decode()
        expected_menu_html = """
        <div id="nav-contact">
            <div class="flat-menu contact no_heading">
                <ul>
                    <li class="">
                        <a href="/contact-us/#offices">Call us</a>
                    </li>
                    <li class="">
                        <a href="#advisor-chat">Chat to an advisor</a>
                    </li>
                    <li class="">
                        <a href="#request-callback">Request a callback</a>
                    </li>
                </ul>
            </div>
        </div>"""
        self.assertHTMLEqual(menu_html, expected_menu_html)

    @override_settings(LANGUAGE_CODE="de",)
    def test_custom_flat_menu_german(self):
        """
        Test that the HTML output by the 'flat_menu' tag (when using the handle
        'contact') renders as expected.
        """
        response = self.client.get('/superheroes/dc-comics/batman/')
        soup = BeautifulSoup(response.content, 'html.parser')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='nav-contact').decode()
        expected_menu_html = """
        <div id="nav-contact">
            <div class="flat-menu contact no_heading">
                <ul>
                    <li class="">
                        <a href="/contact-us/#offices">Rufen Sie uns an</a>
                    </li>
                    <li class="">
                        <a href="#advisor-chat">Chat mit einem Berater</a>
                    </li>
                    <li class="">
                        <a href="#request-callback">Rückruf anfordern</a>
                    </li>
                </ul>
            </div>
        </div>"""
        self.assertHTMLEqual(menu_html, expected_menu_html)
