# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from wagtail import VERSION as WAGTAIL_VERSION
from wagtailmenus import get_main_menu_model, get_flat_menu_model
from wagtailmenus.models import MainMenu, FlatMenu
from wagtailmenus.tests.models import (
    MainMenuCustomMenuItem, FlatMenuCustomMenuItem, NoAbsoluteUrlsPage,
    CustomMainMenu, CustomMainMenuItem, CustomFlatMenu, CustomFlatMenuItem
)
if WAGTAIL_VERSION >= (2, 0):
    from wagtail.core.models import Site
else:
    from wagtail.wagtailcore.models import Site


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
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='main-menu').decode()
        expected_menu_html = """
        <div id="main-menu">
            <ul class="nav navbar-nav">
                <li class=""><a href="/">Home</a></li>
                <li class=" dropdown top-level">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Etwa <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class=" top-level"><a href="/about-us/">Abschnitt zu Hause</a></li>
                        <li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" dropdown top-level">
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
        soup = BeautifulSoup(response.content, 'html5lib')

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
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='main-menu').decode()
        expected_menu_html = """
        <div id="main-menu">
            <ul class="nav navbar-nav">
                <li class=""><a href="/">Home</a></li>
                <li class=" dropdown top-level">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Sur <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class=" top-level"><a href="/about-us/">Section accueil</a></li>
                        <li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" dropdown top-level">
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
        soup = BeautifulSoup(response.content, 'html5lib')

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
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='main-menu').decode()
        expected_menu_html = """
        <div id="main-menu">
            <ul class="nav navbar-nav">
                <li class=""><a href="/">Home</a></li>
                <li class=" dropdown top-level">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class=" top-level"><a href="/about-us/">Section home</a></li>
                        <li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" dropdown top-level">
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
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='main-menu').decode()
        expected_menu_html = """
        <div id="main-menu">
            <ul class="nav navbar-nav">
                <li class=""><a href="/">Home</a></li>
                <li class=" dropdown top-level">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Etwa <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class=" top-level"><a href="/about-us/">Abschnitt zu Hause</a></li>
                        <li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" dropdown top-level">
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
        soup = BeautifulSoup(response.content, 'html5lib')

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
        soup = BeautifulSoup(response.content, 'html5lib')

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

    @override_settings(WAGTAILMENUS_CHILDREN_MENU_CLASS='wagtailmenus.tests.models.CustomChildrenMenu',)
    def test_children_menu_override(self):
        from wagtailmenus.conf import settings
        from wagtailmenus.tests.models import CustomChildrenMenu
        self.assertEqual(
            settings.get_object('CHILDREN_MENU_CLASS'),
            CustomChildrenMenu
        )

        # check that template specified with the classes 'template_name'
        # attribute is the one that gets picked up
        response = self.client.get('/about-us/')
        self.assertTemplateUsed(response, "menus/custom-overrides/children.html")

    @override_settings(WAGTAILMENUS_SECTION_MENU_CLASS='wagtailmenus.tests.models.CustomSectionMenu', )
    def test_section_menu_override(self):
        from wagtailmenus.conf import settings
        from wagtailmenus.tests.models import CustomSectionMenu
        self.assertEqual(
            settings.get_object('SECTION_MENU_CLASS'),
            CustomSectionMenu
        )

        # check that template specified with the classes
        # 'sub_menu_template_name' attribute gets picked up
        response = self.client.get('/about-us/')
        self.assertTemplateUsed(response, "menus/custom-overrides/section-sub.html")


class TestInvalidCustomMenuModels(TestCase):
    fixtures = ['test.json', 'test_custom_models.json']

    @override_settings(WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME='invalid_related_name',)
    def test_invalid_main_menu_items_related_name(self):
        with self.assertRaisesMessage(ImproperlyConfigured, (
            "'invalid_related_name' isn't a valid relationship name for "
            "accessing menu items from MainMenu."
        )):
            menu = get_main_menu_model().objects.get(id=1)
            menu.get_menu_items_manager()

    @override_settings(WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME='invalid_related_name',)
    def test_invalid_flat_menu_items_related_name(self):
        with self.assertRaisesMessage(ImproperlyConfigured, (
            "'invalid_related_name' isn't a valid relationship name for "
            "accessing menu items from FlatMenu."
        )):
            menu = get_flat_menu_model().objects.get(id=1)
            menu.get_menu_items_manager()

    @override_settings(WAGTAILMENUS_MAIN_MENU_MODEL='CustomMainMenu',)
    def test_main_menu_invalid_format(self):
        with self.assertRaisesMessage(ImproperlyConfigured, (
                "WAGTAILMENUS_MAIN_MENU_MODEL must be in the format "
                "'app_label.model_name'"
        )):
            get_main_menu_model()

    @override_settings(WAGTAILMENUS_MAIN_MENU_MODEL='tests.NonExistentMainMenu',)
    def test_main_menu_no_existent(self):
        with self.assertRaisesMessage(ImproperlyConfigured, (
            "WAGTAILMENUS_MAIN_MENU_MODEL refers to model "
            "'tests.NonExistentMainMenu' that has not been installed"
        )):
            get_main_menu_model()

    @override_settings(WAGTAILMENUS_FLAT_MENU_MODEL='CustomFlatMenu',)
    def test_flat_menu_invalid_format(self):
        with self.assertRaisesMessage(ImproperlyConfigured, (
            "WAGTAILMENUS_FLAT_MENU_MODEL must be in the format "
            "'app_label.model_name'"
        )):
            get_flat_menu_model()

    @override_settings(WAGTAILMENUS_FLAT_MENU_MODEL='tests.NonExistentFlatMenu',)
    def test_flat_menu_no_existent(self):
        with self.assertRaisesMessage(ImproperlyConfigured, (
            "WAGTAILMENUS_FLAT_MENU_MODEL refers to model "
            "'tests.NonExistentFlatMenu' that has not been installed"
        )):
            get_flat_menu_model()

    @override_settings(WAGTAILMENUS_CHILDREN_MENU_CLASS='CustomChildrenMenu',)
    def test_children_menu_invalid_path(self):
        from wagtailmenus.conf import settings
        with self.assertRaisesMessage(ImproperlyConfigured, (
            "'CustomChildrenMenu' is not a valid import path. "
            "WAGTAILMENUS_CHILDREN_MENU_CLASS must be a full dotted "
            "python import path e.g. 'project.app.module.Class'"
        )):
            settings.get_object('CHILDREN_MENU_CLASS')

    @override_settings(WAGTAILMENUS_SECTION_MENU_CLASS='CustomSectionMenu',)
    def test_section_menu_invalid_path(self):
        from wagtailmenus.conf import settings
        with self.assertRaisesMessage(ImproperlyConfigured, (
            "'CustomSectionMenu' is not a valid import path. "
            "WAGTAILMENUS_SECTION_MENU_CLASS must be a full dotted "
            "python import path e.g. 'project.app.module.Class'"
        )):
            settings.get_object('SECTION_MENU_CLASS')


class TestNoAbsoluteUrlsPage(TestCase):

    def setUp(self):
        self.site = Site.objects.select_related('root_page').get(is_default_site=True)
        self.no_absolute_urls_page = NoAbsoluteUrlsPage(
            title='Compatibility Test Page',
        )
        self.site.root_page.add_child(instance=self.no_absolute_urls_page)
