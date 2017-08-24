from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from wagtail.wagtailcore import hooks
from bs4 import BeautifulSoup


class TestHooks(TestCase):
    fixtures = ['test.json']

    def test_menus_modify_menu_items(self):

        # NOTE: Positional args used to ensure supplied args remain consistent
        @hooks.register('menus_modify_menu_items')
        def modify_menu_items(
            menu_items, request, parent_page, original_menu_tag, menu_instance,
            current_level, max_levels, stop_at_this_level, current_site,
            current_page, use_specific, apply_active_classes,
            allow_repeating_parents, use_absolute_page_urls
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
        del hooks._hooks['menus_modify_menu_items']

        # If the the hook failed to recieve any of the arguments defined
        # on `modify_menu_items` above, there will be an error
        self.assertEqual(response.status_code, 200)

        # There are 4 main menus being output, and because our hook only adds
        # the additional item to the first level of each of those, the
        # 'VISIT RKH.CO.UK' text should appear exactly 4 times
        self.assertContains(response, 'VISIT RKH.CO.UK', 4)

    def test_menus_modify_base_page_queryset(self):

        # NOTE: Positional args used to ensure supplied args remain consistent
        @hooks.register('menus_modify_base_page_queryset')
        def modify_page_queryset(
            queryset, request, menu_type, root_page, max_levels, use_specific,
            menu_instance
        ):
            """
            Nullify page queryset for 'flat menus'. Should result in only
            links to custom urls being rendered.
            """
            if menu_type == 'flat_menu':
                queryset = queryset.none()
            return queryset

        # Let's render the test homepage to see what happens!
        response = self.client.get('/')

        # unhook asap to prevent knock-on effects on failure
        del hooks._hooks['menus_modify_base_page_queryset']

        # If the the hook failed to recieve any of the arguments defined
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
            queryset, request, menu_type, root_page, max_levels, use_specific,
            menu_instance
        ):
            """
            Nullify menu items completely for all 'flat menus'. Should result
            in completely empty menus
            """
            if menu_type == 'flat_menu':
                queryset = queryset.none()
            return queryset

        # Let's render the test homepage to see what happens!
        response = self.client.get('/')

        # unhook asap to prevent knock-on effects on failure
        del hooks._hooks['menus_modify_base_menuitem_queryset']

        # If the the hook failed to recieve any of the arguments defined
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
