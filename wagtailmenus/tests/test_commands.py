from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from django.core.management import call_command
from wagtail.wagtailcore.models import Site

from wagtailmenus import app_settings


class TestAutoPopulateMainMenus(TestCase):
    fixtures = ['test.json']

    def setUp(self):
        super(TestAutoPopulateMainMenus, self).setUp()
        # Delete any existing main menus and their items
        self.model = app_settings.MAIN_MENU_MODEL_CLASS
        self.model.objects.all().delete()

    def test_without_home_links(self):
        call_command('autopopulate_main_menus', add_home_links=False)
        site = Site.objects.all().first()
        menu = self.model.get_for_site(site)
        menu_items = menu.get_menu_items_manager()

        # Confirm that there are menu items
        self.assertTrue(menu_items.count() == 5)

        # Confirm that the first item is NOT a home page link
        self.assertFalse(menu_items.first().menu_text == 'Home')

        # Call the command again to confirm that the already populated
        # menu doesn't gain any more items
        call_command('autopopulate_main_menus', add_home_links=False)
        self.assertTrue(menu_items.count() == 5)

    def test_with_home_links(self):
        call_command('autopopulate_main_menus', add_home_links=True)
        site = Site.objects.all().first()
        menu = self.model.get_for_site(site)
        menu_items = menu.get_menu_items_manager()

        # Confirm that there are menu items
        self.assertTrue(menu_items.count() == 6)

        # Confirm that the first item is a home page link
        self.assertTrue(menu_items.first().menu_text == 'Home')

        # Call the command again to confirm that the already populated
        # menu doesn't gain any more items
        call_command('autopopulate_main_menus', add_home_links=True)
        self.assertTrue(menu_items.count() == 6)
