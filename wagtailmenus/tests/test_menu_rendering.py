from bs4 import BeautifulSoup
from django.test import TestCase, override_settings
from wagtail import VERSION as WAGTAIL_VERSION
if WAGTAIL_VERSION >= (2, 0):
    from wagtail.core.models import Site
else:
    from wagtail.wagtailcore.models import Site
from wagtailmenus.errors import SubMenuUsageError
from wagtailmenus.models import MainMenu, FlatMenu
from wagtailmenus.templatetags.menu_tags import validate_supplied_values



class TestTemplateTags(TestCase):
    fixtures = ['test.json']
    maxDiff = None

    def test_main_menu_created_when_not_exists(self):
        menu = MainMenu.objects.get(pk=1)
        self.assertEqual(menu.__str__(), 'Main menu for wagtailmenus (co.uk)')
        menu.delete()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        menu = MainMenu.objects.first()
        self.assertTrue(menu)
        self.assertEqual(menu.__str__(), 'Main menu for wagtailmenus (co.uk)')

    def test_flat_menu_get_for_site_with_default_fallback(self):
        site_one = Site.objects.get(pk=1)
        site_two = Site.objects.get(pk=2)

        # Site one (default) definitiely has a menu defined with the handle
        # `footer`
        menu = FlatMenu.get_for_site('footer', site_one)
        site_one_menu_pk = menu.pk
        self.assertIsNotNone(menu)

        # Site two doesn't have any menus defined, so this should return None
        menu = FlatMenu.get_for_site('footer', site_two)
        self.assertIsNone(menu)

        # But if we use the `use_default_site_menu_as_fallback` flag to fetch
        # from the default site, we should get the one defined for site_one
        menu = FlatMenu.get_for_site('footer', site_two, True)
        self.assertIsNotNone(menu)
        self.assertEqual(menu.pk, site_one_menu_pk)

    def test_validate_supplied_values(self):
        with self.assertRaisesMessage(ValueError, 'The `main_menu` tag expects `max_levels` to be an integer value between 1 and 5. Please review your template.'):
            validate_supplied_values(tag='main_menu', max_levels=9)

        with self.assertRaisesMessage(ValueError, 'The `main_menu` tag expects `max_levels` to be an integer value between 1 and 5. Please review your template.'):
            validate_supplied_values(tag='main_menu', max_levels='1')

        with self.assertRaisesMessage(ValueError, 'The `main_menu` tag expects `use_specific` to be an integer value between 0 and 3. Please review your template.'):
            validate_supplied_values(tag='main_menu', use_specific=5)

        with self.assertRaisesMessage(ValueError, 'The `main_menu` tag expects `use_specific` to be an integer value between 0 and 3. Please review your template.'):
            validate_supplied_values(tag='main_menu', use_specific='2')

        with self.assertRaises(ValueError):
            validate_supplied_values(tag='main_menu', parent_page=False)

        with self.assertRaises(ValueError):
            validate_supplied_values(tag='main_menu', menuitem_or_page=5)

    def test_homepage(self):
        """
        Test that homepage (based on `MenuPage`) renders without errors.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    @override_settings(WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS=True,)
    def test_about_us(self):
        """
        Test that 'About us' page (based on `MenuPage`), with
        `repeat_in_subnav=True`, renders without errors.

        The `WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS` setting is also
        applied to increase coverage in get_template() and
        get_sub_menu_template() methods.
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
                <li class=" dropdown top-level">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class=" top-level"><a href="/about-us/">Section home</a></li>
                        <li class=" low-level"><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=" low-level"><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=" low-level"><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" dropdown top-level">
                    <a href="/news-and-events/" class="dropdown-toggle" id="ddtoggle_14" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">News &amp; events <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_14">
                        <li class=" low-level"><a href="/news-and-events/latest-news/">Latest news</a></li>
                        <li class=" low-level"><a href="/news-and-events/upcoming-events/">Upcoming events</a></li>
                        <li class=" low-level"><a href="/news-and-events/press/">In the press</a></li>
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
                <li class=" dropdown top-level">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class=" top-level"><a href="/about-us/">Section home</a></li>
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

    def test_homepage_main_menu_absolute_urls(self):
        """
        Test '{{ main_menu use_absolute_page_urls=True }}' output for homepage
        """
        response = self.client.get('/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='main-menu-absolute-url').decode()
        expected_menu_html = """
        <div id="main-menu-absolute-url">
            <ul class="nav navbar-nav">
                <li class="active">
                    <a href="http://www.wagtailmenus.co.uk:8000/">Home</a>
                </li>
                <li class=" dropdown top-level">
                    <a href="http://www.wagtailmenus.co.uk:8000/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class=" top-level">
                            <a href="http://www.wagtailmenus.co.uk:8000/about-us/">Section home</a>
                        </li>
                        <li class="">
                            <a href="http://www.wagtailmenus.co.uk:8000/about-us/meet-the-team/">Meet the team</a>
                        </li>
                        <li class="">
                            <a href="http://www.wagtailmenus.co.uk:8000/about-us/our-heritage/">Our heritage</a>
                        </li>
                        <li class="">
                            <a href="http://www.wagtailmenus.co.uk:8000/about-us/mission-and-values/">Our mission and values</a>
                        </li>
                    </ul>
                </li>
                <li class=" dropdown top-level">
                    <a href="http://www.wagtailmenus.co.uk:8000/news-and-events/" class="dropdown-toggle" id="ddtoggle_14" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">News &amp; events <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_14">
                        <li class="">
                            <a href="http://www.wagtailmenus.co.uk:8000/news-and-events/latest-news/">Latest news</a>
                        </li>
                        <li class="">
                            <a href="http://www.wagtailmenus.co.uk:8000/news-and-events/upcoming-events/">Upcoming events</a>
                        </li>
                        <li class="">
                            <a href="http://www.wagtailmenus.co.uk:8000/news-and-events/press/">In the press</a>
                        </li>
                    </ul>
                </li>
                <li class="">
                    <a href="http://google.co.uk">Google</a>
                </li>
                <li class=" dropdown">
                    <a href="http://www.wagtailmenus.co.uk:8000/contact-us/" class="dropdown-toggle" id="ddtoggle_18" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Contact us <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_18">
                        <li class="support">
                            <a href="/contact-us/#support">Get support</a>
                        </li>
                        <li class="call">
                            <a href="/contact-us/#call">Speak to someone</a>
                        </li>
                        <li class="map">
                            <a href="/contact-us/#map">Map &amp; directions</a>
                        </li>
                    </ul>
                </li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_homepage_children_menu_one_level(self):
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

    def test_homepage_children_menu_three_levels(self):
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

    def test_homepage_children_absolute_urls(self):
        """
        Test '{% children_menu use_absolute_page_urls=True %}' output for homepage
        """
        response = self.client.get('/')
        soup = BeautifulSoup(response.content, 'html5lib')
        menu_html = soup.find(id='children-menu-absolute-url').decode()
        expected_menu_html = """
        <div id="children-menu-absolute-url">
            <ul>
                <li class="">
                    <a href="http://www.wagtailmenus.co.uk:8000/about-us/">About us</a>
                </li>
                <li class="">
                    <a href="http://www.wagtailmenus.co.uk:8000/news-and-events/">News &amp; events</a>
                </li>
                <li class="">
                    <a href="http://www.wagtailmenus.co.uk:8000/contact-us/">Contact us</a>
                </li>
                <li class="">
                    <a href="http://www.wagtailmenus.co.uk:8000/legal/">Legal</a>
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
                <li class="ancestor dropdown top-level">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class="active top-level"><a href="/about-us/">Section home</a></li>
                        <li class=" low-level"><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=" low-level"><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=" low-level"><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" dropdown top-level">
                    <a href="/news-and-events/" class="dropdown-toggle" id="ddtoggle_14" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">News &amp; events <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_14">
                        <li class=" low-level"><a href="/news-and-events/latest-news/">Latest news</a></li>
                        <li class=" low-level"><a href="/news-and-events/upcoming-events/">Upcoming events</a></li>
                        <li class=" low-level"><a href="/news-and-events/press/">In the press</a></li>
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
                <li class="ancestor dropdown top-level">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class="active top-level">
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

    def test_about_us_main_menu_absolute_urls(self):
        """
                Test '{{ main_menu use_absolute_page_urls=True }}' output for homepage
                """
        response = self.client.get('/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='main-menu-absolute-url').decode()
        expected_menu_html = """
            <div id="main-menu-absolute-url">
                <ul class="nav navbar-nav">
                    <li class="active">
                        <a href="http://www.wagtailmenus.co.uk:8000/">Home</a>
                    </li>
                    <li class=" dropdown top-level">
                        <a href="http://www.wagtailmenus.co.uk:8000/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>
                        <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                            <li class=" top-level">
                                <a href="http://www.wagtailmenus.co.uk:8000/about-us/">Section home</a>
                            </li>
                            <li class="">
                                <a href="http://www.wagtailmenus.co.uk:8000/about-us/meet-the-team/">Meet the team</a>
                            </li>
                            <li class="">
                                <a href="http://www.wagtailmenus.co.uk:8000/about-us/our-heritage/">Our heritage</a>
                            </li>
                            <li class="">
                                <a href="http://www.wagtailmenus.co.uk:8000/about-us/mission-and-values/">Our mission and values</a>
                            </li>
                        </ul>
                    </li>
                    <li class=" dropdown top-level">
                        <a href="http://www.wagtailmenus.co.uk:8000/news-and-events/" class="dropdown-toggle" id="ddtoggle_14" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">News &amp; events <span class="caret"></span></a>
                        <ul class="dropdown-menu" aria-labelledby="ddtoggle_14">
                            <li class="">
                                <a href="http://www.wagtailmenus.co.uk:8000/news-and-events/latest-news/">Latest news</a>
                            </li>
                            <li class="">
                                <a href="http://www.wagtailmenus.co.uk:8000/news-and-events/upcoming-events/">Upcoming events</a>
                            </li>
                            <li class="">
                                <a href="http://www.wagtailmenus.co.uk:8000/news-and-events/press/">In the press</a>
                            </li>
                        </ul>
                    </li>
                    <li class="">
                        <a href="http://google.co.uk">Google</a>
                    </li>
                    <li class=" dropdown">
                        <a href="http://www.wagtailmenus.co.uk:8000/contact-us/" class="dropdown-toggle" id="ddtoggle_18" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Contact us <span class="caret"></span></a>
                        <ul class="dropdown-menu" aria-labelledby="ddtoggle_18">
                            <li class="support">
                                <a href="/contact-us/#support">Get support</a>
                            </li>
                            <li class="call">
                                <a href="/contact-us/#call">Speak to someone</a>
                            </li>
                            <li class="map">
                                <a href="/contact-us/#map">Map &amp; directions</a>
                            </li>
                        </ul>
                    </li>
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

    def test_about_us_section_menu_absolute_urls(self):
        """
        Test '{% section_menu use_absolute_page_urls=True %}' output for 'About us' page
        """
        response = self.client.get('/about-us/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='section-menu-absolute-url').decode()
        expected_menu_html = """
        <div id="section-menu-absolute-url">
            <nav class="nav-section" role="navigation">
                    <a href="http://www.wagtailmenus.co.uk:8000/about-us/" class="ancestor section_root">About us</a>
                <ul>
                    <li class="active">
                        <a href="http://www.wagtailmenus.co.uk:8000/about-us/">Section home</a>
                    </li>
                    <li class="">
                        <a href="http://www.wagtailmenus.co.uk:8000/about-us/meet-the-team/">Meet the team</a>
                <ul>
                    <li class="">
                        <a href="http://www.wagtailmenus.co.uk:8000/about-us/meet-the-team/staff-member-one/">Staff member one</a>
                    </li>
                    <li class="">
                        <a href="http://www.wagtailmenus.co.uk:8000/about-us/meet-the-team/staff-member-two/">Staff member two</a>
                    </li>
                    <li class="">
                        <a href="http://www.wagtailmenus.co.uk:8000/about-us/meet-the-team/staff-member-three/">Staff member three</a>
                    </li>
                </ul>
                    </li>
                    <li class="">
                        <a href="http://www.wagtailmenus.co.uk:8000/about-us/our-heritage/">Our heritage</a>
                    </li>
                    <li class="">
                        <a href="http://www.wagtailmenus.co.uk:8000/about-us/mission-and-values/">Our mission and values</a>
                    </li>
                </ul>
            </nav>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_about_us_children_menu_one_level(self):
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

    def test_about_us_children_menu_three_levels(self):
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

    def test_about_us_children_absolute_urls(self):
        """
        Test '{{ sub_menu self }}' output for 'About us' page
        """
        response = self.client.get('/about-us/')
        soup = BeautifulSoup(response.content, 'html5lib')
        menu_html = soup.find(id='children-menu-absolute-urls').decode()
        expected_menu_html = """
        <div id="children-menu-absolute-urls">
            <ul>
                <li class="">
                    <a href="http://www.wagtailmenus.co.uk:8000/about-us/">Section home</a>
                </li>
                <li class="">
                    <a href="http://www.wagtailmenus.co.uk:8000/about-us/meet-the-team/">Meet the team</a>
                </li>
                <li class="">
                    <a href="http://www.wagtailmenus.co.uk:8000/about-us/our-heritage/">Our heritage</a>
                </li>
                <li class="">
                    <a href="http://www.wagtailmenus.co.uk:8000/about-us/mission-and-values/">Our mission and values</a>
                </li>
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

    def test_marvel_comics_section_absolute_urls(self):
        """
        Test '{% section_menu use_absolute_page_urls=True %}' output for 'Marvel comics' page
        """
        response = self.client.get('/superheroes/marvel-comics/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='section-menu-absolute-url').decode()
        expected_menu_html = """
        <div id="section-menu-absolute-url">
            <nav class="nav-section" role="navigation">
                    <a href="http://www.wagtailmenus.co.uk:8000/superheroes/" class="ancestor section_root">Superheroes</a>
                <ul>
                    <li class="active">
                        <a href="http://www.wagtailmenus.co.uk:8000/superheroes/marvel-comics/">Marvel Comics</a>
                <ul>
                    <li class="">
                        <a href="http://www.wagtailmenus.co.uk:8000/superheroes/marvel-comics/iron-man/">Iron Man</a>
                    </li>
                    <li class="">
                        <a href="http://www.wagtailmenus.co.uk:8000/superheroes/marvel-comics/spiderman/">Spiderman</a>
                    </li>
                </ul>
                    </li>
                    <li class="">
                        <a href="http://www.wagtailmenus.co.uk:8000/superheroes/dc-comics/">D.C. Comics</a>
                <ul>
                    <li class="">
                        <a href="http://www.wagtailmenus.co.uk:8000/superheroes/dc-comics/batman/">Batman</a>
                    </li>
                    <li class="">
                        <a href="http://www.wagtailmenus.co.uk:8000/superheroes/dc-comics/wonder-woman/">Wonder Woman</a>
                    </li>
                </ul>
                    </li>
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
        expected_menu_html = """
        <div id="nav-footer">
            <div class="flat-menu footer with_heading">
                <h4>Important links</h4>
                <ul>
                    <li class=""><a href="/legal/accessibility/">Accessibility</a></li>
                    <li class=""><a href="/legal/privacy-policy/">Privacy policy</a></li>
                    <li class=""><a href="/legal/terms-and-conditions/">Terms and conditions</a></li>
                    <li class=""><a href="/about-us/meet-the-team/custom-url/">Meet the team's pets</a></li>
                </ul>
            </div>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

        response = self.client.get('/legal/privacy-policy/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='nav-footer').decode()
        expected_menu_html = """
        <div id="nav-footer">
            <div class="flat-menu footer with_heading">
                <h4>Important links</h4>
                <ul>
                    <li class=""><a href="/legal/accessibility/">Accessibility</a></li>
                    <li class="active"><a href="/legal/privacy-policy/">Privacy policy</a></li>
                    <li class=""><a href="/legal/terms-and-conditions/">Terms and conditions</a></li>
                    <li class=""><a href="/about-us/meet-the-team/custom-url/">Meet the team's pets</a></li>
                </ul>
            </div>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

        response = self.client.get('/about-us/meet-the-team/custom-url/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='nav-footer').decode()
        expected_menu_html = """
        <div id="nav-footer">
            <div class="flat-menu footer with_heading">
                <h4>Important links</h4>
                <ul>
                    <li class=""><a href="/legal/accessibility/">Accessibility</a></li>
                    <li class=""><a href="/legal/privacy-policy/">Privacy policy</a></li>
                    <li class=""><a href="/legal/terms-and-conditions/">Terms and conditions</a></li>
                    <li class="active"><a href="/about-us/meet-the-team/custom-url/">Meet the team's pets</a></li>
                </ul>
            </div>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

        response = self.client.get('/')
        soup = BeautifulSoup(response.content, 'html5lib')

        # Assertions to compare rendered HTML against expected HTML
        menu_html = soup.find(id='nav-footer-absolute-urls').decode()
        expected_menu_html = """
        <div id="nav-footer-absolute-urls">
            <div class="flat-menu footer with_heading">
                <h4>Important links</h4>
                <ul>
                    <li class="">
                        <a href="http://www.wagtailmenus.co.uk:8000/legal/accessibility/">Accessibility</a>
                    </li>
                    <li class="">
                        <a href="http://www.wagtailmenus.co.uk:8000/legal/privacy-policy/">Privacy policy</a>
                    </li>
                    <li class="">
                        <a href="http://www.wagtailmenus.co.uk:8000/legal/terms-and-conditions/">Terms and conditions</a>
                    </li>
                    <li class="">
                        <a href="/about-us/meet-the-team/custom-url/">Meet the team's pets</a>
                    </li>
                </ul>
            </div>
        </div>
        """
        self.assertHTMLEqual(menu_html, expected_menu_html)

    def test_custom_page_menu_output(self):
        response = self.client.get('/custom-url/')
        soup = BeautifulSoup(response.content, 'html5lib')

        main_menu_html = soup.find(id='main-menu-two-levels').decode()
        expected_menu_html = """
        <div id="main-menu-two-levels">
            <ul class="nav navbar-nav">
                <li class=""><a href="/">Home</a></li>
                <li class=" dropdown top-level">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class=" top-level"><a href="/about-us/">Section home</a></li>
                        <li class=" low-level"><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=" low-level"><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=" low-level"><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" dropdown top-level">
                    <a href="/news-and-events/" class="dropdown-toggle" id="ddtoggle_14" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">News &amp; events <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_14">
                        <li class=" low-level"><a href="/news-and-events/latest-news/">Latest news</a></li>
                        <li class=" low-level"><a href="/news-and-events/upcoming-events/">Upcoming events</a></li>
                        <li class=" low-level"><a href="/news-and-events/press/">In the press</a></li>
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
                <li class="ancestor dropdown top-level">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class=" top-level"><a href="/about-us/">Section home</a></li>
                        <li class="ancestor low-level"><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=" low-level"><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=" low-level"><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" dropdown top-level">
                    <a href="/news-and-events/" class="dropdown-toggle" id="ddtoggle_14" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">News &amp; events <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_14">
                        <li class=" low-level"><a href="/news-and-events/latest-news/">Latest news</a></li>
                        <li class=" low-level"><a href="/news-and-events/upcoming-events/">Upcoming events</a></li>
                        <li class=" low-level"><a href="/news-and-events/press/">In the press</a></li>
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
                <li class="ancestor dropdown top-level">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>
                    <ul class="dropdown-menu" aria-labelledby="ddtoggle_6">
                        <li class=" top-level">
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

    @override_settings(WAGTAILMENUS_SITE_SPECIFIC_TEMPLATE_DIRS=True)
    def test_use_specific_off(self):
        """
        The below URL is a custom URL, but the URL matches a real page,
        which will be indicated in the menus being output. It's using a
        template where use_specific=0 is supplied to all menu tags, so
        there should be no repeating items, no programatically added
        items, and no additional classes present on <li> elements
        """
        response = self.client.get('/superheroes/marvel-comics/iron-man/')
        soup = BeautifulSoup(response.content, 'html5lib')

        main_menu_html = soup.find(id='main-menu').decode()
        expected_main_menu_html = """
        <div id="main-menu">
            <ul class="nav navbar-nav">
                <li class="">
                    <a href="/">Home</a>
                </li>
                <li class=" dropdown">
                    <a href="/about-us/" class="dropdown-toggle" id="ddtoggle_6" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">About <span class="caret"></span></a>  
                    <ul aria-labelledby="ddtoggle_6" class="dropdown-menu">
                        <li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" dropdown">
                    <a href="/news-and-events/" class="dropdown-toggle" id="ddtoggle_14" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">News &amp; events <span class="caret"></span></a>
                    <ul aria-labelledby="ddtoggle_14" class="dropdown-menu">
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
        self.assertHTMLEqual(main_menu_html, expected_main_menu_html)

        seconday_nav_html = soup.find(id='secondary-nav').decode()
        expected_seconday_nav_html = """
        <div id="secondary-nav">
            <ul>
                <li class="">
                    <a href="/about-us/">About us</a>
                    <ul class="sub-menu" data-level="2">
                        <li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=""><a href="/superheroes/marvel-comics/">Marvel Comics</a></li>
                <li class=""><a href="/superheroes/dc-comics/">D.C. Comics</a></li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(seconday_nav_html, expected_seconday_nav_html)

        section_menu_html = soup.find(id='section-menu').decode()
        expected_section_menu_html = """
        <div id="section-menu">
            <a href="/superheroes/" class="ancestor section_root">Superheroes</a>
            <ul>
                <li class="ancestor">
                    <a href="/superheroes/marvel-comics/">Marvel Comics</a>
                    <ul class="sub-menu" data-level="2">
                        <li class="active"><a href="/superheroes/marvel-comics/iron-man/">Iron Man</a></li>
                        <li class=""><a href="/superheroes/marvel-comics/spiderman/">Spiderman</a></li>
                    </ul>
                </li>
                <li class="">
                    <a href="/superheroes/dc-comics/">D.C. Comics</a>
                    <ul class="sub-menu" data-level="2">
                        <li class=""><a href="/superheroes/dc-comics/batman/">Batman</a></li>
                        <li class=""><a href="/superheroes/dc-comics/wonder-woman/">Wonder Woman</a></li>
                    </ul>
                </li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(section_menu_html, expected_section_menu_html)

    def test_use_specific_top_level(self):
        """
        The below URL is a custom URL, but the URL matches a real page,
        which will be indicated in the menus being output. It's using a
        template where use_specific=2 is supplied to all menu tags, most of the
        first level <li> elements should have additional classes from their
        respective specific model, and should see repeated items and
        programatically added items too.
        """
        response = self.client.get('/superheroes/dc-comics/batman/')
        soup = BeautifulSoup(response.content, 'html5lib')

        main_menu_html = soup.find(id='main-menu').decode()
        expected_main_menu_html = """
        <div id="main-menu">
            <ul class="nav navbar-nav">
                <li class=""><a href="/">Home</a></li>
                <li class=" dropdown top-level">
                    <a aria-expanded="false" aria-haspopup="true" class="dropdown-toggle" data-toggle="dropdown" href="/about-us/" id="ddtoggle_6">About <span class="caret"></span></a>
                    <ul aria-labelledby="ddtoggle_6" class="dropdown-menu">
                        <li class=" top-level"><a href="/about-us/">Section home</a></li>
                        <li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" dropdown top-level">
                    <a aria-expanded="false" aria-haspopup="true" class="dropdown-toggle" data-toggle="dropdown" href="/news-and-events/" id="ddtoggle_14">News &amp; events <span class="caret"></span></a>
                    <ul aria-labelledby="ddtoggle_14" class="dropdown-menu">
                        <li class=""><a href="/news-and-events/latest-news/">Latest news</a></li>
                        <li class=""><a href="/news-and-events/upcoming-events/">Upcoming events</a></li>
                        <li class=""><a href="/news-and-events/press/">In the press</a></li>
                    </ul>
                </li>
                <li class=""><a href="http://google.co.uk">Google</a></li>
                <li class=" dropdown">
                    <a aria-expanded="false" aria-haspopup="true" class="dropdown-toggle" data-toggle="dropdown" href="/contact-us/" id="ddtoggle_18">Contact us <span class="caret"></span></a>
                    <ul aria-labelledby="ddtoggle_18" class="dropdown-menu">
                        <li class="support"><a href="/contact-us/#support">Get support</a></li>
                        <li class="call"><a href="/contact-us/#call">Speak to someone</a></li>
                        <li class="map"><a href="/contact-us/#map">Map &amp; directions</a></li>
                    </ul>
                </li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(main_menu_html, expected_main_menu_html)

        seconday_nav_html = soup.find(id='secondary-nav').decode()
        expected_seconday_nav_html = """
        <div id="secondary-nav">
            <ul>
                <li class=" top-level">
                    <a href="/about-us/">About us</a>
                    <ul class="sub-menu" data-level="2">
                        <li class=" top-level"><a href="/about-us/">Section home</a></li>
                        <li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" low-level"><a href="/superheroes/marvel-comics/">Marvel Comics</a></li>
                <li class=" low-level"><a href="/superheroes/dc-comics/">D.C. Comics</a></li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(seconday_nav_html, expected_seconday_nav_html)

        section_menu_html = soup.find(id='section-menu').decode()
        expected_section_menu_html = """
        <div id="section-menu">
            <a href="/superheroes/" class="ancestor section_root top-level">Superheroes</a>
            <ul>
                <li class="">
                    <a href="/superheroes/marvel-comics/">Marvel Comics</a>
                    <ul class="sub-menu" data-level="2">
                        <li class=""><a href="/superheroes/marvel-comics/iron-man/">Iron Man</a></li>
                        <li class=""><a href="/superheroes/marvel-comics/spiderman/">Spiderman</a></li>
                    </ul>
                </li>
                <li class="ancestor">
                    <a href="/superheroes/dc-comics/">D.C. Comics</a>
                    <ul class="sub-menu" data-level="2">
                        <li class="active"><a href="/superheroes/dc-comics/batman/">Batman</a></li>
                        <li class=""><a href="/superheroes/dc-comics/wonder-woman/">Wonder Woman</a></li>
                    </ul>
                </li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(section_menu_html, expected_section_menu_html)

    def test_use_specific_always(self):
        """
        The below URL is a custom URL, but the URL matches a real page,
        which will be indicated in the menus being output. It's using a
        template where use_specific=3 is supplied to all menu tags, so all
        <li> elements should have additional classes from their
        respective specific model.
        """
        response = self.client.get('/superheroes/dc-comics/wonder-woman/')
        soup = BeautifulSoup(response.content, 'html5lib')

        main_menu_html = soup.find(id='main-menu').decode()
        expected_main_menu_html = """
        <div id="main-menu">
            <ul class="nav navbar-nav">
                <li class=""><a href="/">Home</a></li>
                <li class=" dropdown top-level">
                    <a aria-expanded="false" aria-haspopup="true" class="dropdown-toggle" data-toggle="dropdown" href="/about-us/" id="ddtoggle_6">About <span class="caret"></span></a>
                    <ul aria-labelledby="ddtoggle_6" class="dropdown-menu">
                        <li class=" top-level"><a href="/about-us/">Section home</a></li>
                        <li class=" low-level"><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=" low-level"><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=" low-level"><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" dropdown top-level">
                    <a aria-expanded="false" aria-haspopup="true" class="dropdown-toggle" data-toggle="dropdown" href="/news-and-events/" id="ddtoggle_14">News &amp; events <span class="caret"></span></a>
                    <ul aria-labelledby="ddtoggle_14" class="dropdown-menu">
                        <li class=" low-level"><a href="/news-and-events/latest-news/">Latest news</a></li>
                        <li class=" low-level"><a href="/news-and-events/upcoming-events/">Upcoming events</a></li>
                        <li class=" low-level"><a href="/news-and-events/press/">In the press</a></li>
                    </ul>
                </li>
                <li class=""><a href="http://google.co.uk">Google</a></li>
                <li class=" dropdown">
                    <a aria-expanded="false" aria-haspopup="true" class="dropdown-toggle" data-toggle="dropdown" href="/contact-us/" id="ddtoggle_18">Contact us <span class="caret"></span></a>
                    <ul aria-labelledby="ddtoggle_18" class="dropdown-menu">
                        <li class="support"><a href="/contact-us/#support">Get support</a></li>
                        <li class="call"><a href="/contact-us/#call">Speak to someone</a></li>
                        <li class="map"><a href="/contact-us/#map">Map &amp; directions</a></li>
                    </ul>
                </li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(main_menu_html, expected_main_menu_html)

        seconday_nav_html = soup.find(id='secondary-nav').decode()
        expected_seconday_nav_html = """
        <div id="secondary-nav">
            <ul>
                <li class=" top-level">
                    <a href="/about-us/">About us</a>
                    <ul class="sub-menu" data-level="2">
                        <li class=" top-level"><a href="/about-us/">Section home</a></li>
                        <li class=" low-level"><a href="/about-us/meet-the-team/">Meet the team</a></li>
                        <li class=" low-level"><a href="/about-us/our-heritage/">Our heritage</a></li>
                        <li class=" low-level"><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    </ul>
                </li>
                <li class=" low-level"><a href="/superheroes/marvel-comics/">Marvel Comics</a></li>
                <li class=" low-level"><a href="/superheroes/dc-comics/">D.C. Comics</a></li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(seconday_nav_html, expected_seconday_nav_html)

        section_menu_html = soup.find(id='section-menu').decode()
        expected_section_menu_html = """
        <div id="section-menu">
            <a href="/superheroes/" class="ancestor section_root top-level">Superheroes</a>
            <ul>
                <li class=" low-level">
                    <a href="/superheroes/marvel-comics/">Marvel Comics</a>
                    <ul class="sub-menu" data-level="2">
                        <li class=" low-level"><a href="/superheroes/marvel-comics/iron-man/">Iron Man</a></li>
                        <li class=" low-level"><a href="/superheroes/marvel-comics/spiderman/">Spiderman</a></li>
                    </ul>
                </li>
                <li class="ancestor low-level">
                    <a href="/superheroes/dc-comics/">D.C. Comics</a>
                    <ul class="sub-menu" data-level="2">
                        <li class=" low-level"><a href="/superheroes/dc-comics/batman/">Batman</a></li>
                        <li class="active low-level"><a href="/superheroes/dc-comics/wonder-woman/">Wonder Woman</a></li>
                    </ul>
                </li>
            </ul>
        </div>
        """
        self.assertHTMLEqual(section_menu_html, expected_section_menu_html)

    def test_sub_menu_tag_usage_in_non_menu_template_raises_submenuusageerror(self):
        """
        The 'sub_menu' tag should raise an error if used directly (not from
        within another menu template)
        """
        with self.assertRaises(SubMenuUsageError):
            self.client.get('/sub_menu-tag-used-directly/')


@override_settings(WAGTAILMENUS_USE_BACKEND_SPECIFIC_TEMPLATES=True)
class TestRenderingWithBackendSpecificTemplates(TestTemplateTags):
    pass
