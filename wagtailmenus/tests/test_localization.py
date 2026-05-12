"""
Tests for the LOCALIZE_MENU_ITEMS feature (closes #242).

These tests verify that when `WAGTAILMENUS_LOCALIZE_MENU_ITEMS = True` (or
`WAGTAIL_I18N_ENABLED = True`) is configured:

- ``AbstractMenuItem.__init__`` swaps ``link_page`` to its active-locale
  counterpart so that ``menu_text`` / ``href`` are locale-aware.
- ``get_pages_for_display()`` builds the prefetch queryset from the
  localized page tree, so multi-level submenus are populated correctly.
- The final page filter correctly bridges the locale gap (the N+1 query
  path based on ``p.localized.id``) instead of a direct queryset
  intersection that would be empty when locales differ.
- All existing behaviour is preserved when the setting is disabled.
"""

from unittest.mock import patch

from django.test import TestCase, override_settings
from wagtail.models import Page

from wagtailmenus.conf import settings
from wagtailmenus.models import MainMenu, MainMenuItem


# ---------------------------------------------------------------------------
# Helper: a descriptor that replaces Page.localized during a test
# ---------------------------------------------------------------------------

class _LocalizedMapping:
    """
    Descriptor that replaces ``Page.localized`` for the duration of a test.

    ``mapping`` is a dict of {original_page_id: localized_page}.  Any page
    whose id is not in the mapping simply returns itself (i.e. already in
    the active locale).
    """

    def __init__(self, mapping):
        self.mapping = mapping

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.mapping.get(obj.pk, obj)


# ---------------------------------------------------------------------------
# 1.  Setting configuration
# ---------------------------------------------------------------------------

class TestLocalizationSetting(TestCase):
    """LOCALIZE_MENU_ITEMS setting defaults and auto-detection."""

    def test_disabled_by_default(self):
        self.assertFalse(settings.LOCALIZE_MENU_ITEMS)

    @override_settings(WAGTAILMENUS_LOCALIZE_MENU_ITEMS=True)
    def test_explicit_override_enables_feature(self):
        self.assertTrue(settings.LOCALIZE_MENU_ITEMS)

    @override_settings(WAGTAILMENUS_LOCALIZE_MENU_ITEMS=False)
    def test_explicit_false_disables_feature(self):
        self.assertFalse(settings.LOCALIZE_MENU_ITEMS)

    @override_settings(WAGTAIL_I18N_ENABLED=True)
    def test_auto_detection_from_wagtail_i18n_enabled(self):
        self.assertTrue(settings.LOCALIZE_MENU_ITEMS)

    @override_settings(WAGTAIL_I18N_ENABLED=True, WAGTAILMENUS_LOCALIZE_MENU_ITEMS=False)
    def test_explicit_false_overrides_wagtail_i18n_enabled(self):
        """An explicit opt-out must not be overridden by WAGTAIL_I18N_ENABLED."""
        self.assertFalse(settings.LOCALIZE_MENU_ITEMS)

    @override_settings(WAGTAIL_I18N_ENABLED=False)
    def test_auto_detection_returns_false_when_wagtail_i18n_disabled(self):
        self.assertFalse(settings.LOCALIZE_MENU_ITEMS)


# ---------------------------------------------------------------------------
# 2.  get_top_level_items() locale swap (render-time, not __init__-time)
# ---------------------------------------------------------------------------

class TestMenuItemLocalizationRenderTime(TestCase):
    """
    Localization is applied at render time by get_top_level_items(), not in
    AbstractMenuItem.__init__. This means the stored FK is never mutated so
    admin saves cannot accidentally persist the swapped value.
    """

    fixtures = ['test.json']

    # --- disabled (default) -------------------------------------------------

    def test_top_level_items_link_page_unchanged_when_disabled(self):
        """When the feature is off, link_page is whatever is stored."""
        menu = MainMenu.objects.get(pk=1)
        first_item = menu.get_menu_items_manager().filter(
            link_page__isnull=False
        ).first()
        item_pk = first_item.pk
        original_page_pk = first_item.link_page_id

        # Even with a localization mapping active, link_page must not be swapped
        other_page = Page.objects.exclude(pk=original_page_pk).filter(
            live=True, expired=False, show_in_menus=True
        ).first()
        mapping = _LocalizedMapping({original_page_pk: other_page})
        with patch.object(Page, 'localized', mapping):
            items = menu.get_top_level_items()

        # Identify the item by its menu item pk (stable; not the page FK)
        matched = [i for i in items if getattr(i, 'pk', None) == item_pk]
        self.assertTrue(len(matched) > 0)
        self.assertEqual(matched[0].link_page.pk, original_page_pk)

    # --- enabled ------------------------------------------------------------

    @override_settings(WAGTAILMENUS_LOCALIZE_MENU_ITEMS=True)
    def test_top_level_items_link_page_swapped_when_enabled(self):
        """When localization is on, item.link_page is set to the localized page."""
        menu = MainMenu.objects.get(pk=1)
        first_item = menu.get_menu_items_manager().filter(
            link_page__isnull=False
        ).first()
        item_pk = first_item.pk  # stable menu item pk, not the page FK
        en_page = first_item.link_page
        it_page = Page.objects.exclude(pk=en_page.pk).filter(
            live=True, expired=False, show_in_menus=True
        ).first()

        mapping = _LocalizedMapping({en_page.pk: it_page})
        with patch.object(Page, 'localized', mapping):
            items = menu.get_top_level_items()

        # After the swap, link_page_id is updated to it_page.pk by Django's FK
        # descriptor, so identify the item by its stable menu item pk instead.
        matched = [i for i in items if getattr(i, 'pk', None) == item_pk]
        self.assertTrue(len(matched) > 0)
        self.assertEqual(matched[0].link_page.pk, it_page.pk)

    @override_settings(WAGTAILMENUS_LOCALIZE_MENU_ITEMS=True)
    def test_stored_link_page_id_not_mutated_by_render(self):
        """The FK column (link_page_id) must not change after get_top_level_items()."""
        menu = MainMenu.objects.get(pk=1)
        first_item = menu.get_menu_items_manager().filter(
            link_page__isnull=False
        ).first()
        en_page = first_item.link_page
        it_page = Page.objects.exclude(pk=en_page.pk).filter(
            live=True, expired=False, show_in_menus=True
        ).first()

        mapping = _LocalizedMapping({en_page.pk: it_page})
        with patch.object(Page, 'localized', mapping):
            menu.get_top_level_items()

        # Re-read the item from DB: the FK must still be the original en page
        stored = menu.get_menu_items_manager().get(pk=first_item.pk)
        self.assertEqual(stored.link_page_id, en_page.pk)

    @override_settings(WAGTAILMENUS_LOCALIZE_MENU_ITEMS=True)
    def test_top_level_items_unchanged_when_already_in_active_locale(self):
        """When localized returns the same page (already active locale), nothing changes."""
        menu = MainMenu.objects.get(pk=1)
        # Empty mapping → all pages return themselves
        mapping = _LocalizedMapping({})
        with patch.object(Page, 'localized', mapping):
            items = menu.get_top_level_items()
        self.assertEqual(len(items), 5)

    @override_settings(WAGTAILMENUS_LOCALIZE_MENU_ITEMS=True)
    def test_top_level_items_no_op_when_link_page_is_none(self):
        """Custom URL items (no link_page) are always included unchanged."""
        menu = MainMenu.objects.get(pk=1)
        mapping = _LocalizedMapping({})
        with patch.object(Page, 'localized', mapping):
            items = menu.get_top_level_items()
        url_items = [i for i in items if not getattr(i, 'link_page_id', None)]
        # All URL-only items must still be present
        for item in url_items:
            self.assertIsNone(item.link_page)


# ---------------------------------------------------------------------------
# 3.  get_pages_for_display – locale-aware queryset building
# ---------------------------------------------------------------------------

class TestGetPagesForDisplayLocalization(TestCase):
    """
    get_pages_for_display() returns localized pages when the feature is on.
    """

    fixtures = ['test.json']

    def _get_menu_and_first_item_pages(self):
        """Return (menu, en_page, it_page) where it_page != en_page."""
        menu = MainMenu.objects.get(pk=1)
        # Pick the first item that has a link_page
        first_item = menu.get_menu_items_manager().filter(
            link_page__isnull=False
        ).first()
        en_page = first_item.link_page
        # Use any *other* live page as the fake localized counterpart
        it_page = Page.objects.exclude(pk=en_page.pk).filter(
            live=True, expired=False, show_in_menus=True
        ).first()
        return menu, en_page, it_page

    # --- disabled (default) -------------------------------------------------

    def test_pages_for_display_unchanged_when_disabled(self):
        menu = MainMenu.objects.get(pk=1)
        # The fixture has 12 pages for this menu
        self.assertEqual(len(menu.pages_for_display), 12)

    # --- enabled: localized page is included --------------------------------

    @override_settings(WAGTAILMENUS_LOCALIZE_MENU_ITEMS=True)
    def test_pages_for_display_includes_localized_page(self):
        """
        When localization is active and a localized page exists, it must
        appear in pages_for_display (keyed by the localized page id, which
        is what __init__ sets as link_page_id after the swap).
        """
        menu, en_page, it_page = self._get_menu_and_first_item_pages()

        # Map: en_page → it_page; everything else stays the same
        mapping = _LocalizedMapping({en_page.pk: it_page})

        with patch.object(Page, 'localized', mapping):
            # Bypass the @cached_property so we get a fresh result
            pages = menu.get_pages_for_display()
            page_ids = {p.id for p in pages}

        self.assertIn(it_page.pk, page_ids)

    @override_settings(WAGTAILMENUS_LOCALIZE_MENU_ITEMS=True)
    def test_pages_for_display_excludes_original_when_localized_differs(self):
        """
        When the localized page is different, the original (en) page should
        not be in pages_for_display unless it is also linked elsewhere.
        """
        menu, en_page, it_page = self._get_menu_and_first_item_pages()

        # Only the single-page (no allow_subnav) case for a clean assertion:
        # find an item where allow_subnav is False
        item = menu.get_menu_items_manager().filter(
            link_page__isnull=False, allow_subnav=False
        ).first()
        if item is None:
            self.skipTest("No allow_subnav=False item in fixture")

        en_page = item.link_page
        # Pick a page not otherwise in the menu as the fake translation
        menu_page_ids = set(
            menu.get_menu_items_manager().values_list('link_page_id', flat=True)
        )
        it_page = Page.objects.filter(
            live=True, expired=False, show_in_menus=True
        ).exclude(pk__in=menu_page_ids).first()
        if it_page is None:
            self.skipTest("Not enough pages in fixture for this test")

        mapping = _LocalizedMapping({en_page.pk: it_page})

        with patch.object(Page, 'localized', mapping):
            pages = menu.get_pages_for_display()
            page_ids = {p.id for p in pages}

        # Original en_page should NOT appear; localized it_page SHOULD
        self.assertNotIn(en_page.pk, page_ids)
        self.assertIn(it_page.pk, page_ids)

    # --- enabled: same-locale is a no-op ------------------------------------

    @override_settings(WAGTAILMENUS_LOCALIZE_MENU_ITEMS=True)
    def test_pages_for_display_unchanged_when_already_in_active_locale(self):
        """
        When Page.localized returns the same page (already in active locale)
        the output of get_pages_for_display() must be identical to the
        non-localization case.
        """
        menu = MainMenu.objects.get(pk=1)

        # Empty mapping → all pages return themselves
        mapping = _LocalizedMapping({})
        with patch.object(Page, 'localized', mapping):
            pages = menu.get_pages_for_display()

        # Still the same 12 pages
        self.assertEqual(len(pages), 12)


# ---------------------------------------------------------------------------
# 4.  Regression: existing behaviour preserved when disabled
# ---------------------------------------------------------------------------

class TestLocalizationRegressionWhenDisabled(TestCase):
    """
    The full top_level_items / pages_for_display pipeline must behave
    identically to before when LOCALIZE_MENU_ITEMS is False (the default).
    """

    fixtures = ['test.json']

    def test_top_level_items_count_unchanged(self):
        menu = MainMenu.objects.get(pk=1)
        # Fixture has 6 menu items, one of which links to show_in_menus=False
        # so 5 top-level items are returned
        self.assertEqual(len(menu.top_level_items), 5)

    def test_pages_for_display_count_unchanged(self):
        menu = MainMenu.objects.get(pk=1)
        self.assertEqual(len(menu.pages_for_display), 12)

    def test_pages_for_display_all_live_and_show_in_menus(self):
        menu = MainMenu.objects.get(pk=1)
        for page in menu.pages_for_display.values():
            self.assertTrue(page.live)
            self.assertFalse(page.expired)
            self.assertTrue(page.show_in_menus)
