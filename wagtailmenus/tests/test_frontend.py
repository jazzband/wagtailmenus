from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from django.core.exceptions import ValidationError

from wagtail.wagtailcore.models import Page
from wagtailmenus.models import MainMenu, MainMenuItem, FlatMenu
from bs4 import BeautifulSoup


class TestModels(TestCase):
    fixtures = ['test.json']

    def test_mainmenuitem_clean_missing_link_text(self):
        menu = MainMenu.objects.get(pk=1)
        new_item = MainMenuItem(menu=menu, link_url='test/')
        self.assertRaisesMessage(
            ValidationError,
            "This must be set if you're linking to a custom URL.",
            new_item.clean)

    def test_mainmenuitem_clean_missing_link_url(self):
        menu = MainMenu.objects.get(pk=1)
        new_item = MainMenuItem(menu=menu)
        self.assertRaisesMessage(
            ValidationError,
            "This must be set if you're not linking to a page.",
            new_item.clean)

    def test_mainmenuitem_clean_link_url_and_link_page(self):
        menu = MainMenu.objects.get(pk=1)
        new_item = MainMenuItem(menu=menu, link_text='Test', link_url='test/', link_page=Page.objects.get(pk=6))
        self.assertRaisesMessage(
            ValidationError,
            "You cannot link to both a page and URL. Please review your link and clear any unwanted values.",
            new_item.clean)

    def test_mainmenuitem_str(self):
        menu = MainMenu.objects.get(pk=1)
        item_1 = menu.menu_items.first()
        self.assertEqual(item_1.__str__(), 'Home')

    def test_flatmenuitem_str(self):
        menu = FlatMenu.objects.get(handle='contact')
        item_1 = menu.menu_items.first()
        self.assertEqual(item_1.__str__(), 'Call us')


class TestTemplateTags(TestCase):
    fixtures = ['test.json']
    maxDiff = None

    def test_main_menu_created_when_not_exists(self):
        menu = MainMenu.objects.get(pk=1)
        self.assertEqual(menu.__str__(), 'Main menu for Test')
        menu.delete()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        menu = MainMenu.objects.first()
        self.assertTrue(menu)
        self.assertEqual(menu.__str__(), 'Main menu for Test')

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

    def test_marvel_comics(self):
        """
        Test that 'Marvel comics' page (based on `Page`), and within a
        section with subnav, renders without errors.
        """
        response = self.client.get('/superheroes/marvel-comics/')
        self.assertEqual(response.status_code, 200)

    def test_staff_vacancies(self):
        """
        Test that 'Staff vacancies' page (based on `Page`), with
        `show_in_menus=False`, and within a section with subnav, renders
        without errors.
        """
        response = self.client.get('/about-us/staff-vacancies/')
        self.assertEqual(response.status_code, 200)

    def test_non_page(self):
        """
        Test that there are no errors when rendering page template without
        the `wagtailmenus.wagtail_hooks.wagtailmenu_params_helper()` method
        having run to add helpful bits to the context.
        """
        response = self.client.get('/custom-url/')
        self.assertEqual(response.status_code, 200)

    def test_homepage_main_menu_two_levels(self):
        """
        Test '{{ main_menu }}' output for homepage
        """
        response = self.client.get('/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='main-menu-two-levels').decode()
        expected_menu_html = """
        <div id="main-menu-two-levels">
            <ul class="nav navbar-nav">
                <li class="active"><a href="/">Home</a></li>
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
                <li class=""><a href="/contact-us/">Contact us</a></li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_homepage_main_menu_three_levels(self):
        """
        Test '{{ main_menu max_levels=3 }}' output for homepage
        """
        response = self.client.get('/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='main-menu-three-levels').decode()
        expected_menu_html = """
        <div id="main-menu-three-levels">
            <ul class="nav navbar-nav">
                <li class="active"><a href="/">Home</a></li>
                <li class=" dropdown">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class=""><a href="/about-us/">Section home</a></li>
                        <li class=" dropdown">
                            <a href="/about-us/meet-the-team/" class="dropdown-toggle" id="ddtoggle_7" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Meet the team <span class="caret"></span></a>
                            <ul class="dropdown-menu" aria-labelledby="ddtoggle_7">
                                <li class=""><a href="/about-us/meet-the-team/staff-member-one/">Staff member one</a></li>
                                <li class=""><a href="/about-us/meet-the-team/staff-member-two/">Staff member two</a></li>
                                <li class=""><a href="/about-us/meet-the-team/staff-member-three/">Staff member three</a></li>
                            </ul>
                        </li>
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
                <li class=""><a href="/contact-us/">Contact us</a></li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_homepage_sub_menu_one_level(self):
        """
        Test '{% children_menu %}' output for homepage
        """
        response = self.client.get('/')
        soup = BeautifulSoup(response.content, 'html5lib')
        menu_html = soup.find(id='children-menu-one-level').decode()
        expected_menu_html = """
        <div id="children-menu-one-level">
            <ul>
                <li class=""><a href="/about-us/">About us</a></li>
                <li class=""><a href="/news-and-events/">News &amp; events</a></li>
                <li class=""><a href="/contact-us/">Contact us</a></li>
                <li class=""><a href="/legal/">Legal</a></li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_homepage_sub_menu_three_levels(self):
        """
        Test '{% children_menu max_levels=3 allow_repeating_parents=False %}' output for homepage
        """
        response = self.client.get('/')
        soup = BeautifulSoup(response.content, 'html5lib')
        menu_html = soup.find(id='children-menu-three-levels').decode()
        expected_menu_html = """
        <div id="children-menu-three-levels">
            <ul>
                <li class=""><a href="/about-us/">About us</a>
                    <ul>
                        <li class="">
                            <a href="/about-us/meet-the-team/">Meet the team</a>
                            <ul>
                                <li class=""><a href="/about-us/meet-the-team/staff-member-one/">Staff member one</a></li>
                                <li class=""><a href="/about-us/meet-the-team/staff-member-two/">Staff member two</a></li>
                                <li class=""><a href="/about-us/meet-the-team/staff-member-three/">Staff member three</a></li>
                            </ul>
                        </li>
                        <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class="">
                    <a href="/news-and-events/">News &amp; events</a>
                    <ul>
                        <li class=""><a href="/news-and-events/latest-news/">Latest news</a></li>
                        <li class=""><a href="/news-and-events/upcoming-events/">Upcoming events</a></li>
                        <li class=""><a href="/news-and-events/press/">In the press</a></li>
                    </ul>
                </li>
                <li class=""><a href="/contact-us/">Contact us</a></li>
                <li class="">
                    <a href="/legal/">Legal</a>
                    <ul>
                        <li class=""><a href="/legal/accessibility/">Accessibility</a></li>
                        <li class=""><a href="/legal/privacy-policy/">Privacy policy</a></li>
                        <li class=""><a href="/legal/terms-and-conditions/">Terms and conditions</a></li>
                    </ul>
                </li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_about_us_main_menu_two_levels(self):
        """
        Test '{% main_menu %}' output for 'About us' page
        """
        response = self.client.get('/about-us/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='main-menu-two-levels').decode()
        expected_menu_html = """
        <div id="main-menu-two-levels">
            <ul class="nav navbar-nav">
                <li class=""><a href="/">Home</a></li>
                <li class="ancestor dropdown">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class="active"><a href="/about-us/">Section home</a></li>
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
                <li class=""><a href="/contact-us/">Contact us</a></li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_about_us_main_menu_three_levels(self):
        """
        Test '{% main_menu max_levels=3 %}' output for 'About us' page
        """
        response = self.client.get('/about-us/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='main-menu-three-levels').decode()
        expected_menu_html = """
        <div id="main-menu-three-levels">
            <ul class="nav navbar-nav">
                <li class=""><a href="/">Home</a></li>
                <li class="ancestor dropdown">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class="active">
                            <a href="/about-us/">Section home</a>
                        </li>
                        <li class=" dropdown">
                            <a href="/about-us/meet-the-team/" class="dropdown-toggle" id="ddtoggle_7" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Meet the team <span class="caret"></span></a>
                            <ul class="dropdown-menu" aria-labelledby="ddtoggle_7">
                                <li class=""><a href="/about-us/meet-the-team/staff-member-one/">Staff member one</a></li>
                                <li class=""><a href="/about-us/meet-the-team/staff-member-two/">Staff member two</a></li>
                                <li class=""><a href="/about-us/meet-the-team/staff-member-three/">Staff member three</a></li>
                            </ul>
                        </li>
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
                <li class=""><a href="/contact-us/">Contact us</a></li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_about_us_section_menu_two_levels(self):
        """
        Test '{% section_menu %}' output for 'About us' page
        """
        response = self.client.get('/about-us/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='section-menu-two-levels').decode()
        expected_menu_html = """
        <div id="section-menu-two-levels">
            <nav class="nav-section" role="navigation">
                <a href="/about-us/" class="ancestor section_root">About us</a>
                <ul>
                    <li class="active"><a href="/about-us/">Section home</a></li>
                    <li class="">
                        <a href="/about-us/meet-the-team/">Meet the team</a>
                        <ul>
                            <li class=""><a href="/about-us/meet-the-team/staff-member-one/">Staff member one</a></li>
                            <li class=""><a href="/about-us/meet-the-team/staff-member-two/">Staff member two</a></li>
                            <li class=""><a href="/about-us/meet-the-team/staff-member-three/">Staff member three</a></li>
                        </ul>
                    </li>
                    <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                    <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                </ul>
            </nav>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_about_us_section_menu_one_level(self):
        """
        Test '{% section_menu max_levels=1 %}' output for 'About us' page
        """
        response = self.client.get('/about-us/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='section-menu-one-level').decode()
        expected_menu_html = """
        <div id="section-menu-one-level">
            <nav class="nav-section" role="navigation">
                <a href="/about-us/" class="ancestor section_root">About us</a>
                <ul>
                    <li class="active"><a href="/about-us/">Section home</a></li>
                    <li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li>
                    <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                    <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                </ul>
            </nav>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_about_us_sub_menu_one_level(self):
        """
        Test '{{ sub_menu self }}' output for 'About us' page
        """
        response = self.client.get('/about-us/')
        soup = BeautifulSoup(response.content, 'html5lib')
        menu_html = soup.find(id='children-menu-one-level').decode()
        expected_menu_html = """
        <div id="children-menu-one-level">
            <ul>
                <li class=""><a href="/about-us/">Section home</a></li>
                <li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li>
                <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_about_us_sub_menu_three_levels(self):
        """
        Test '{% children_menu max_levels=3 allow_repeating_parents=False %}' output for 'About us' page
        """
        response = self.client.get('/about-us/')
        soup = BeautifulSoup(response.content, 'html5lib')
        menu_html = soup.find(id='children-menu-three-levels').decode()
        expected_menu_html = """
        <div id="children-menu-three-levels">
            <ul>
                <li class="">
                    <a href="/about-us/meet-the-team/">Meet the team</a>
                    <ul>
                        <li class=""><a href="/about-us/meet-the-team/staff-member-one/">Staff member one</a></li>
                        <li class=""><a href="/about-us/meet-the-team/staff-member-two/">Staff member two</a></li>
                        <li class=""><a href="/about-us/meet-the-team/staff-member-three/">Staff member three</a></li>
                    </ul>
                </li>
                <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_marvel_comics_section_menu_two_levels(self):
        """
        Test '{% section_menu %}' output for 'Marvel comics' page
        """
        response = self.client.get('/superheroes/marvel-comics/')
        soup = BeautifulSoup(response.content, 'html5lib')

        menu_html = soup.find(id='section-menu-two-levels').decode()
        expected_menu_html = """
        <div id="section-menu-two-levels">
            <nav class="nav-section" role="navigation">
                <a href="/superheroes/" class="ancestor section_root">Superheroes</a>
                <ul>
                    <li class="active">
                        <a href="/superheroes/marvel-comics/">Marvel Comics</a>
                        <ul>
                            <li class=""><a href="/superheroes/marvel-comics/iron-man/">Iron Man</a></li>
                            <li class=""><a href="/superheroes/marvel-comics/spiderman/">Spiderman</a></li>
                        </ul>
                    </li>
                    <li class="">
                        <a href="/superheroes/dc-comics/">D.C. Comics</a>
                        <ul>
                            <li class=""><a href="/superheroes/dc-comics/batman/">Batman</a></li>
                            <li class="">
                                <a href="/superheroes/dc-comics/wonder-woman/">Wonder Woman</a>
                            </li>
                        </ul>
                    </li>
                </ul>
            </nav>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_marvel_comics_section_menu_one_level(self):
        """
        Test '{% section_menu max_levels=1 %}' output for 'Marvel comics' page
        """
        response = self.client.get('/superheroes/marvel-comics/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='section-menu-one-level').decode()
        expected_menu_html = """
        <div id="section-menu-one-level">
            <nav class="nav-section" role="navigation">
                <a href="/superheroes/" class="ancestor section_root">Superheroes</a>
                <ul>
                    <li class="active"><a href="/superheroes/marvel-comics/">Marvel Comics</a></li>
                    <li class=""><a href="/superheroes/dc-comics/">D.C. Comics</a></li>
                </ul>
            </nav>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_contact_flat_menu_output(self):
        """
        Test that the HTML output by the 'flat_menu' tag (when using the handle 'contact') renders as expected.
        """
        response = self.client.get('/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='nav-contact').decode()
        expected_menu_html = """<div id="nav-contact"><div class="flat-menu contact no_heading"><ul><li class=""><a href="/contact-us/#offices">Call us</a></li><li class=""><a href="#advisor-chat">Chat to an advisor</a></li><li class=""><a href="#request-callback">Request a callback</a></li></ul></div></div>"""
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_footer_flat_menu_output(self):
        """
        Test that the HTML output by the 'flat_menu' tag (when using the handle 'footer') renders as expected.
        """
        response = self.client.get('/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='nav-footer').decode()
        expected_menu_html = """<div id="nav-footer"><div class="flat-menu footer with_heading"><h4>Important links</h4><ul><li class=""><a href="/legal/accessibility/">Accessibility</a></li><li class=""><a href="/legal/privacy-policy/">Privacy policy</a></li><li class=""><a href="/legal/terms-and-conditions/">Terms and conditions</a></li></ul></div></div>"""
        self.assertHTMLEqual(menu_html, expected_menu_html)

        response = self.client.get('/legal/privacy-policy/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='nav-footer').decode()
        expected_menu_html = """<div id="nav-footer"><div class="flat-menu footer with_heading"><h4>Important links</h4><ul><li class=""><a href="/legal/accessibility/">Accessibility</a></li><li class="active"><a href="/legal/privacy-policy/">Privacy policy</a></li><li class=""><a href="/legal/terms-and-conditions/">Terms and conditions</a></li></ul></div></div>"""
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_custom_page_menu_output(self):
        response = self.client.get('/custom-url/')
        soup = BeautifulSoup(response.content, 'html5lib')

        main_menu_html = soup.find(id='main-menu-two-levels').decode()
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
                <li class=""><a href="/contact-us/">Contact us</a></li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(main_menu_html, expected_menu_html)

        section_menu_html = soup.find(id='section-menu-two-levels').decode()
        expected_menu_html = """<div id="section-menu-two-levels"></div>"""
        self.assertHTMLEqual(section_menu_html, expected_menu_html)

    def test_custom_about_us_url_section_menu_two_levels(self):
        """
        Test '{% section_menu max_levels=2 %}' output for a custom url that
        looks like a page from the 'about us' section, but isn't.

        'about-us' and 'meet-the-team' items should be identified as
        'ancestors', as indicated by the request path.
        """
        response = self.client.get('/about-us/meet-the-team/custom-url/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='section-menu-two-levels').decode()
        expected_menu_html = """
        <div id="section-menu-two-levels">
            <nav class="nav-section" role="navigation">
                <a href="/about-us/" class="ancestor section_root">About us</a>
                <ul>
                    <li class=""><a href="/about-us/">Section home</a></li>
                    <li class="ancestor">
                        <a href="/about-us/meet-the-team/">Meet the team</a>
                        <ul>
                            <li class=""><a href="/about-us/meet-the-team/staff-member-one/">Staff member one</a></li>
                            <li class=""><a href="/about-us/meet-the-team/staff-member-two/">Staff member two</a></li>
                            <li class=""><a href="/about-us/meet-the-team/staff-member-three/">Staff member three</a></li>
                        </ul>
                    </li>
                    <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                    <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                </ul>
            </nav>
        </div>
        """
        self.assertEqual(response.status_code, 200)
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_custom_about_us_url_main_menu_two_levels(self):
        """
        Test '{% main_menu max_levels=2 %}' output for a custom url that
        looks like a page from the 'about us' section, but isn't.

        'about-us' and 'meet-the-team' items should be identified as
        'ancestors', as indicated by the request path.
        """
        response = self.client.get('/about-us/meet-the-team/custom-url/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='main-menu-two-levels').decode()
        expected_menu_html = """
        <div id="main-menu-two-levels">
            <ul class="nav navbar-nav">
                <li class=""><a href="/">Home</a></li>
                <li class="ancestor dropdown">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class=""><a href="/about-us/">Section home</a></li>
                        <li class="ancestor"><a href="/about-us/meet-the-team/">Meet the team</a></li>
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
                <li class=""><a href="/contact-us/">Contact us</a></li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_custom_superheroes_url_section_menu_two_levels(self):
        """
        Test '{% section_menu max_levels=2 %}' output for a custom url that
        looks like a page from the superheroes section, but isn't.

        'superheroes' and 'marvel-comics' items should be identified as
        'ancestors', as indicated by the request path.
        """
        response = self.client.get('/superheroes/marvel-comics/custom-man/about/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='section-menu-two-levels').decode()
        expected_menu_html = """
        <div id="section-menu-two-levels">
            <nav class="nav-section" role="navigation">
                <a href="/superheroes/" class="ancestor section_root">Superheroes</a>
                <ul>
                    <li class="ancestor">
                        <a href="/superheroes/marvel-comics/">Marvel Comics</a>
                        <ul>
                            <li class=""><a href="/superheroes/marvel-comics/iron-man/">Iron Man</a></li>
                            <li class=""><a href="/superheroes/marvel-comics/spiderman/">Spiderman</a></li>
                        </ul>
                    </li>
                    <li class="">
                        <a href="/superheroes/dc-comics/">D.C. Comics</a>
                        <ul>
                            <li class=""><a href="/superheroes/dc-comics/batman/">Batman</a></li>
                            <li class="">
                                <a href="/superheroes/dc-comics/wonder-woman/">Wonder Woman</a>
                            </li>
                        </ul>
                    </li>
                </ul>
            </nav>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_staffmember_direct_url_main_menu(self):
        """
        Test '{% main_menu max_levels=3 %}' when serving the following URL:
        /about-us/meet-the-team/staff-member-one/

        It's a real page in the tree, so we want to identify it and highlight
        it as active, but it's not being served via Wagtail's `serve_page`, so
        the page is identified using the request path.
        """
        response = self.client.get('/about-us/meet-the-team/staff-member-one/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='main-menu-three-levels').decode()
        expected_menu_html = """
        <div id="main-menu-three-levels">
            <ul class="nav navbar-nav">
                <li class=""><a href="/">Home</a></li>
                <li class="ancestor dropdown">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class="">
                            <a href="/about-us/">Section home</a>
                        </li>
                        <li class="ancestor dropdown">
                            <a href="/about-us/meet-the-team/" class="dropdown-toggle" id="ddtoggle_7" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Meet the team <span class="caret"></span></a>
                            <ul class="dropdown-menu" aria-labelledby="ddtoggle_7">
                                <li class="active"><a href="/about-us/meet-the-team/staff-member-one/">Staff member one</a></li>
                                <li class=""><a href="/about-us/meet-the-team/staff-member-two/">Staff member two</a></li>
                                <li class=""><a href="/about-us/meet-the-team/staff-member-three/">Staff member three</a></li>
                            </ul>
                        </li>
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
                <li class=""><a href="/contact-us/">Contact us</a></li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_staffmember_direct_url_section_menu(self):
        """
        Test '{% section_menu max_levels=2 %}' when serving the following URL:
        /about-us/meet-the-team/staff-member-one/

        It's a real page in the tree, so we want to identify it and highlight
        it as active, but it's not being served via Wagtail's `serve_page`, so
        the page is identified using the request path.
        """
        response = self.client.get('/about-us/meet-the-team/staff-member-one/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='section-menu-two-levels').decode()
        expected_menu_html = """
        <div id="section-menu-two-levels">
            <nav class="nav-section" role="navigation">
                <a href="/about-us/" class="ancestor section_root">About us</a>
                <ul>
                    <li class=""><a href="/about-us/">Section home</a></li>
                    <li class="ancestor">
                        <a href="/about-us/meet-the-team/">Meet the team</a>
                        <ul>
                            <li class="active"><a href="/about-us/meet-the-team/staff-member-one/">Staff member one</a></li>
                            <li class=""><a href="/about-us/meet-the-team/staff-member-two/">Staff member two</a></li>
                            <li class=""><a href="/about-us/meet-the-team/staff-member-three/">Staff member three</a></li>
                        </ul>
                    </li>
                    <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                    <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                </ul>
            </nav>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_news_and_events_section_menu(self):
        """
        Test '{% section_menu max_levels=2 %}' when serving the following URL:
        /news-and-events/

        It's a real page in the tree, so we want to identify it and highlight
        it as active, but it's not being served via Wagtail's `serve_page`, so
        the page is identified using the request path.
        """
        response = self.client.get('/news-and-events/')

        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='section-menu-two-levels').decode()
        expected_menu_html = """
        <div id="section-menu-two-levels">
            <nav class="nav-section" role="navigation">
                <a href="/news-and-events/" class="active section_root">News &amp; events</a>
                <ul>
                    <li class=""><a href="/news-and-events/latest-news/">Latest news</a></li>
                    <li class=""><a href="/news-and-events/upcoming-events/">Upcoming events</a></li>
                    <li class=""><a href="/news-and-events/press/">In the press</a></li>
                </ul>
            </nav>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)
