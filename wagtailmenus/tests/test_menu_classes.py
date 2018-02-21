from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from django.core.exceptions import ValidationError
from wagtail import VERSION as WAGTAIL_VERSION
if WAGTAIL_VERSION >= (2, 0):
    from wagtail.core.models import Page
else:
    from wagtail.wagtailcore.models import Page

from wagtailmenus.models import (
    ChildrenMenu, MainMenu, MainMenuItem, FlatMenu, FlatMenuItem)


class TestMenuClasses(TestCase):
    fixtures = ['test.json']

    def test_mainmenuitem_meta_settings(self):
        opts = MainMenuItem._meta
        self.assertEqual(opts.verbose_name, 'menu item')
        self.assertEqual(opts.verbose_name_plural, 'menu items')
        self.assertEqual(opts.ordering, ('sort_order',))

    def test_flatmenuitem_meta_settings(self):
        opts = FlatMenuItem._meta
        self.assertEqual(opts.verbose_name, 'menu item')
        self.assertEqual(opts.verbose_name_plural, 'menu items')
        self.assertEqual(opts.ordering, ('sort_order',))

    def test_mainmenuitem_clean_missing_link_text(self):
        menu = MainMenu.objects.get(pk=1)
        new_item = MainMenuItem(menu=menu, link_url='test/')
        self.assertRaisesMessage(
            ValidationError,
            "This field is required when linking to a custom URL",
            new_item.clean)

    def test_mainmenuitem_clean_missing_link_url(self):
        menu = MainMenu.objects.get(pk=1)
        new_item = MainMenuItem(menu=menu)
        self.assertRaisesMessage(
            ValidationError,
            "Please choose an internal page or provide a custom URL",
            new_item.clean)

    def test_mainmenuitem_clean_link_url_and_link_page(self):
        menu = MainMenu.objects.get(pk=1)
        new_item = MainMenuItem(
            menu=menu,
            link_text='Test',
            link_url='test/',
            link_page=Page.objects.get(pk=6))
        self.assertRaisesMessage(
            ValidationError,
            "Linking to both a page and custom URL is not permitted",
            new_item.clean)

    def test_mainmenuitem_str(self):
        menu = MainMenu.objects.get(pk=1)
        item_1 = menu.menu_items.first()
        self.assertEqual(item_1.__str__(), 'Home')

    def test_flatmenuitem_str(self):
        menu = FlatMenu.objects.get(handle='contact')
        item_1 = menu.menu_items.first()
        self.assertEqual(item_1.__str__(), 'Call us')

    def test_mainmenu_top_level_items(self):
        menu = MainMenu.objects.get(pk=1)
        # This menu has a `use_specific` value of 1 (AUTO)
        self.assertEqual(menu.use_specific, 1)

        # So, the top-level items it return should all just be custom links
        # or have a `link_page` that is just a vanilla Page object.
        for item in menu.top_level_items:
            self.assertTrue(item.link_page is None or type(item.link_page) is Page)

        # After being called once, top_level_options should be cached, so
        # accessing it again shouldn't trigger any database queries
        with self.assertNumQueries(0):
            for item in menu.top_level_items:
                self.assertTrue(item.link_page or item.link_url)

        # Lets change `use_specific` to 2 (TOP_LEVEL)
        menu.set_use_specific(2)

        # The above should clear the cached value, so if we call
        # top_level_items again, we should get a fresh list of specific pages
        for item in menu.top_level_items:
            self.assertTrue(item.link_page is None or type(item.link_page) is not Page)

        # Lets change `use_specific` to 0 (OFF) again
        menu.set_use_specific(0)

        # Because the work has already been done to fetch specific items, even
        # though we might not need specific items, the cached value should
        # remain in-tact, with no more queries being triggered on recall.
        with self.assertNumQueries(0):
            for item in menu.top_level_items:
                assert item.link_page is None or type(item.link_page) is not Page

    def test_mainmenu_pages_for_display(self):
        menu = MainMenu.objects.get(pk=1)
        # This menu has a `use_specific` value of 1 (AUTO)
        self.assertEqual(menu.use_specific, 1)
        # And a `max_levels` value of 2
        self.assertEqual(menu.max_levels, 2)

        # So, every page returned by `pages_for_display` should just be a
        # vanilla Page object, that is live, not expired and meant to
        # appear in menus
        for p in menu.pages_for_display:
            self.assertEqual(type(p), Page)
            self.assertTrue(p.live)
            self.assertFalse(p.expired)
            self.assertTrue(p.show_in_menus)

        # Their should be 6 pages total
        self.assertEqual(len(menu.pages_for_display), 6)

        # After being called once, pages_for_display should be cached, so
        # accessing it again shouldn't trigger any database queries
        with self.assertNumQueries(0):
            for p in menu.pages_for_display:
                self.assertTrue(p.title)

        # Lets change `use_specific` to 3 (ALWAYS)
        menu.set_use_specific(3)

        # The above should clear the cached value, so if we call
        # pages_for_display again, we should get a fresh list of specific pages
        for p in menu.pages_for_display:
            self.assertNotEqual(type(p), Page)

        # Lets change `max_levels` to 1
        menu.set_max_levels(1)

        # The above should clear the cached value, so if we call
        # pages_for_display again, we it should provide an empty queryset
        self.assertQuerysetEqual(menu.pages_for_display, Page.objects.none())

        # Lets change `max_levels` to 3
        menu.set_max_levels(3)

        # The above should cleare the cached value, and now pages_for_display
        # should reurn 12 pages total to display
        self.assertEqual(len(menu.pages_for_display), 9)

        # As with `top_level_items` Even is we set `use_specific` to a lower
        # value, the cached `pages_for_display` value will not be cleared, as
        # it specific is better than not.
        menu.set_use_specific(1)

        # Because the work has already been done to fetch specific pages, even
        # though we might not need specific items, the cached value should
        # remain in-tact, with no more queries being triggered on recall.
        with self.assertNumQueries(0):
            for p in menu.pages_for_display:
                assert type(p) is not Page

    def test_add_menu_items_for_pages(self):
        menu = MainMenu.objects.get(pk=1)
        # The current number of menu items is 6
        self.assertEqual(menu.get_menu_items_manager().count(), 6)

        # 'Superheroes' has 2 children: 'D.C. Comics' & 'Marvel Comics'
        superheroes_page = Page.objects.get(title="Superheroes")
        children_of_superheroes = superheroes_page.get_children()
        self.assertEqual(children_of_superheroes.count(), 2)

        # Use 'add_menu_items_for_pages' to add pages for the above pages
        menu.add_menu_items_for_pages(children_of_superheroes)

        # The number of menu items should now be 8
        self.assertEqual(menu.get_menu_items_manager().count(), 8)

        # Evaluate menu items to a list
        menu_items = list(menu.get_menu_items_manager().all())

        # The last item should be a link to the 'D.C. Comics' page, and the
        # sort_order on the item should be 7
        dc_item = menu_items.pop()
        self.assertEqual(dc_item.link_page.title, 'D.C. Comics')
        self.assertEqual(dc_item.sort_order, 7)

        # The '2nd to last' item should be a link to the 'Marvel Comics' page,
        # and the sort_order on the item should be 6
        marvel_item = menu_items.pop()
        self.assertEqual(marvel_item.link_page.title, 'Marvel Comics')
        self.assertEqual(marvel_item.sort_order, 6)


class TestChildrenMenu(TestCase):
    fixtures = ['test.json']

    """A test case for testing deprecated behaviour on the ChildrenMenu class
    introduced in v2.5
    """
    def test_init_required_vals(self):
        page = Page.objects.get(url_path='/home/about-us/')

        msg_extract = "'max_levels' must be provided when creating"
        with self.assertRaisesRegex(TypeError, msg_extract):
            ChildrenMenu(page, use_specific=1)

        msg_extract = "'use_specific' must be provided when creating"
        with self.assertRaisesRegex(TypeError, msg_extract):
            ChildrenMenu(page, max_levels=1)
