
.. _recipes:

===========================
Recipes
===========================

.. contents::
    :local:
    :depth: 2


.. _i18n:

Internationalization for main menus
===================================

While wagtailmenus doesn't provide any internationalization support out-of-the-box, you can create your own custom menu with internationalization support.

The example below is useful if your are using either Wagtail's native internationalization support or a package like `wagtail-localize <https://github.com/wagtail/wagtail-localize>`_, where language-specific trees are being automatically synced.

.. code-block:: python
    # models.py
    from modelcluster.fields import ParentalKey
    from django.db import models
    from wagtail.core.models import Page
    from wagtailmenus.conf import settings as wagtail_settings
    from wagtailmenus.models import AbstractMainMenu, AbstractMainMenuItem


    class LocalizedMainMenu(AbstractMainMenu):
    """A Menu that shows the the localized version of the menu items"""

        def get_pages_for_display(self):
            """Returns a queryset of all pages needed to render the menu."""
            if hasattr(self, "_raw_menu_items"):
                # get_top_level_items() may have set this
                menu_items = self._raw_menu_items
            else:
                menu_items = self.get_base_menuitem_queryset()

            # Start with an empty queryset, and expand as needed
            queryset = Page.objects.none()

            for item in (item for item in menu_items if item.link_page):
                if item.link_page.localized:
                    item.link_page = item.link_page.localized

                if (
                    item.allow_subnav
                    and item.link_page.depth >= wagtail_settings.SECTION_ROOT_DEPTH
                ):
                    # If menu item have subpages, add those to the queryset
                    queryset = queryset | Page.objects.filter(
                        path__startswith=item.link_page.path,
                        depth__lt=item.link_page.depth + self.max_levels,
                    )
                else:
                    queryset = queryset | Page.objects.filter(id=item.link_page_id)

            # Filter out pages unsutable display
            queryset = self.get_base_page_queryset() & queryset

            # Always return 'specific' page instances
            return queryset.specific()


    class LocalizedMainMenuItem(AbstractMainMenuItem):
        menu = ParentalKey(
            LocalizedMainMenu,
            on_delete=models.CASCADE,
            related_name=wagtail_settings.MAIN_MENU_ITEMS_RELATED_NAME,
        )

        def __init__(self, *args, **kwargs):
            """
            This makes the menu work seamlessly with multi-language entirely:
            - In the admin you only add the pages once per language, but the
            menu also appears even if you are visiting the page that is in
            another language.
            - The menu item's text is in the current language.
            - The menu item's link point to the right language.
            """
            super().__init__(*args, **kwargs)
            if self.link_page and self.link_page.localized:
                self.link_page = self.link_page.localized
