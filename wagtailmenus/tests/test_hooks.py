from __future__ import absolute_import, unicode_literals

from bs4 import BeautifulSoup
from django.test import TestCase
from wagtail import VERSION as WAGTAIL_VERSION
if WAGTAIL_VERSION >= (2, 0):
    from wagtail.core import hooks
else:
    from wagtail.wagtailcore import hooks


class TestHooks(TestCase):
    fixtures = ['test.json']

    def test_menus_modify_primed_menu_items(self):

        # NOTE: Positional args used to ensure supplied args remain consistent
        @hooks.register('menus_modify_primed_menu_items')
        def modify_menu_items(
            menu_items, request, parent_context, parent_page, menu_instance,
            original_menu_instance, menu_tag, original_menu_tag, current_level,
            max_levels, use_specific, current_site, current_page,
            current_section_root_page, current_page_ancestor_ids,
            apply_active_classes, allow_repeating_parents,
            use_absolute_page_urls
        ):
            if original_menu_tag == 'main_menu' and current_level == 1:
                menu_items.append({
                    'href': 'https://rkh.co.uk',
                    'text': 'VISIT RKH.CO.UK',
                    'active_class': 'external',
                })
            return menu_items

        # Let's render the test homepage to see what happens!
        response = self.client.get('/')

        # unhook asap to prevent knock-on effects on failure
        del hooks._hooks['menus_modify_primed_menu_items']

        # If the the hook failed to receive any of the arguments defined
        # on `modify_menu_items` above, there will be an error
        self.assertEqual(response.status_code, 200)

        # There are 4 main menus being output, and because our hook only adds
        # the additional item to the first level of each of those, the
        # 'VISIT RKH.CO.UK' text should appear exactly 4 times
        self.assertContains(response, 'VISIT RKH.CO.UK', 4)

    def test_menus_modify_raw_menu_items(self):

        # NOTE: Positional args used to ensure supplied args remain consistent
        @hooks.register('menus_modify_raw_menu_items')
        def modify_menu_items(
            menu_items, request, parent_context, parent_page, menu_instance,
            original_menu_instance, menu_tag, original_menu_tag, current_level,
            max_levels, use_specific, current_site, current_page,
            current_section_root_page, current_page_ancestor_ids,
            apply_active_classes, allow_repeating_parents,
            use_absolute_page_urls
        ):
            if original_menu_tag == 'section_menu' and current_level == 1:
                """
                For the first level of section menus, add a copy of the first
                page to the end of the list
                """
                try:
                    menu_items.append(menu_items[0])
                except KeyError:
                    pass
            return menu_items

        # Let's render the 'about us' page to see what happens!
        response = self.client.get('/about-us/')

        # unhook asap to prevent knock-on effects on failure
        del hooks._hooks['menus_modify_raw_menu_items']

        # If the the hook failed to receive any of the arguments defined
        # on `modify_menu_items` above, there will be an error
        self.assertEqual(response.status_code, 200)

        # Test output reflects hook changes
        soup = BeautifulSoup(response.content, 'html5lib')
        section_menu_html = soup.find(id='section-menu-one-level').decode()
        # 'Call us' is a page link, so should no longer appear
        expected_html = """
        <div id="section-menu-one-level">
            <nav class="nav-section" role="navigation">
                <a href="/about-us/" class="ancestor section_root">About us</a>
                <ul>
                    <li class="active"><a href="/about-us/">Section home</a></li>
                    <li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li>
                    <li class=""><a href="/about-us/our-heritage/">Our heritage</a></li>
                    <li class=""><a href="/about-us/mission-and-values/">Our mission and values</a></li>
                    <li class=""><a href="/about-us/meet-the-team/">Meet the team</a></li>
                </ul>
            </nav>
        </div>
        """
        self.assertHTMLEqual(section_menu_html, expected_html)

    def test_menus_modify_base_page_queryset(self):

        # NOTE: Positional args used to ensure supplied args remain consistent
        @hooks.register('menus_modify_base_page_queryset')
        def modify_page_queryset(
            queryset, request, parent_context, parent_page, menu_instance,
            original_menu_instance, menu_tag, original_menu_tag, current_level,
            max_levels, use_specific, current_site, current_page,
            current_section_root_page, current_page_ancestor_ids,
            apply_active_classes, allow_repeating_parents,
            use_absolute_page_urls
        ):
            """
            Nullify page queryset for 'flat menus'. Should result in only
            links to custom urls being rendered.
            """
            if menu_tag == 'flat_menu':
                queryset = queryset.none()
            return queryset

        # Let's render the test homepage to see what happens!
        response = self.client.get('/')

        # unhook asap to prevent knock-on effects on failure
        del hooks._hooks['menus_modify_base_page_queryset']

        # If the the hook failed to receive any of the arguments defined
        # on `modify_menu_items` above, there will be an error
        self.assertEqual(response.status_code, 200)

        # Test output reflects hook changes
        soup = BeautifulSoup(response.content, 'html5lib')
        contact_menu_html = soup.find(id='nav-contact').decode()
        # 'Call us' is a page link, so should no longer appear
        expected_html = """
        <div id="nav-contact">
            <div class="flat-menu contact no_heading">
                <ul>
                    <li class=""><a href="#advisor-chat">Chat to an advisor</a></li>
                    <li class=""><a href="#request-callback">Request a callback</a></li>
                </ul>
            </div>
        </div>
        """
        self.assertHTMLEqual(contact_menu_html, expected_html)

    def test_menus_modify_base_menuitem_queryset(self):

        # NOTE: Positional args used to ensure supplied args remain consistent
        @hooks.register('menus_modify_base_menuitem_queryset')
        def modify_menuitem_queryset(
            queryset, request, parent_context, parent_page, menu_instance,
            original_menu_instance, menu_tag, original_menu_tag, current_level,
            max_levels, use_specific, current_site, current_page,
            current_section_root_page, current_page_ancestor_ids,
            apply_active_classes, allow_repeating_parents,
            use_absolute_page_urls
        ):
            """
            Nullify menu items completely for all 'flat menus'. Should result
            in completely empty menus
            """
            if menu_tag == 'flat_menu':
                queryset = queryset.none()
            return queryset

        # Let's render the test homepage to see what happens!
        response = self.client.get('/')

        # unhook asap to prevent knock-on effects on failure
        del hooks._hooks['menus_modify_base_menuitem_queryset']

        # If the the hook failed to receive any of the arguments defined
        # on `modify_menu_items` above, there will be an error
        self.assertEqual(response.status_code, 200)

        # Test output reflects hook changes
        soup = BeautifulSoup(response.content, 'html5lib')
        contact_menu_html = soup.find(id='nav-contact').decode()
        # There should be no menu items, so just an empty div (no <ul>)
        expected_html = """
        <div id="nav-contact">
            <div class="flat-menu contact no_heading"></div>
        </div>
        """
        self.assertHTMLEqual(contact_menu_html, expected_html)
