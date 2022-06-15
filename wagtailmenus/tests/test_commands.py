from django.test import TestCase
from django.core.management import call_command
from wagtailmenus.conf import settings
try:
    from wagtail.models import Site
except ImportError:
    from wagtail.core.models import Site


class TestAutoPopulateMainMenus(TestCase):
    fixtures = ['test.json']

    def setUp(self):
        super().setUp()
        # Delete any existing main menus and their items
        self.model = settings.models.MAIN_MENU_MODEL
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

        # Confirm that the the menu items remain unaffected if the command
        # happens to be run more than once
        call_command('autopopulate_main_menus', add_home_links=False)
        menu = self.model.get_for_site(site)
        menu_items2 = menu.get_menu_items_manager()
        self.assertEqual(list(menu_items.all()), list(menu_items2.all()))

    def test_with_home_links(self):
        call_command('autopopulate_main_menus', add_home_links=True)
        site = Site.objects.all().first()
        menu = self.model.get_for_site(site)
        menu_items = menu.get_menu_items_manager()

        # Confirm that there are menu items
        self.assertTrue(menu_items.count() == 6)

        # Confirm that the first item is a home page link
        self.assertTrue(menu_items.first().menu_text == 'Home')

        # Confirm that the the menu items remain unaffected if the command
        # happens to be run more than once
        call_command('autopopulate_main_menus', add_home_links=True)
        menu = self.model.get_for_site(site)
        menu_items2 = menu.get_menu_items_manager()
        self.assertEqual(list(menu_items.all()), list(menu_items2.all()))
