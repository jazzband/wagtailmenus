from __future__ import absolute_import, unicode_literals

from copy import copy

from django.db import models
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailcore.models import Page

from .. import app_settings
from ..panels import menupage_settings_panels


class MenuPage(Page):
    repeat_in_subnav = models.BooleanField(
        verbose_name=_("repeat in sub-navigation"),
        default=False,
        help_text=_(
            "If checked, a link to this page will be repeated alongside it's "
            "direct children when displaying a sub-navigation for this page."
        ),
    )
    repeated_item_text = models.CharField(
        verbose_name=_('repeated item link text'),
        max_length=255,
        blank=True,
        help_text=_(
            "e.g. 'Section home' or 'Overview'. If left blank, the page title "
            "will be used."
        )
    )

    settings_panels = menupage_settings_panels

    class Meta:
        abstract = True

    def modify_submenu_items(
        self, menu_items, current_page, current_ancestor_ids, current_site,
        allow_repeating_parents, apply_active_classes, original_menu_tag,
        menu_instance
    ):
        """
        Make any necessary modifications to `menu_items` and return the list
        back to the calling menu tag to render in templates. Any additional
        items added should have a `text` and `href` attribute as a minimum.

        `original_menu_tag` should be one of 'main_menu', 'section_menu' or
        'children_menu', which should be useful when extending/overriding.
        """
        if (allow_repeating_parents and menu_items and self.repeat_in_subnav):
            """
            This page should have a version of itself repeated alongside
            children in the subnav, so we create a new item and prepend it to
            menu_items.
            """
            menu_items.insert(0, self.get_repeated_menu_item(
                current_page, current_site, apply_active_classes,
                original_menu_tag
            ))
        return menu_items

    def has_submenu_items(
        self, current_page, allow_repeating_parents, original_menu_tag,
        menu_instance
    ):
        """
        When rendering pages in a menu template a `has_children_in_menu`
        attribute is added to each page, letting template developers know
        whether or not the item has a submenu that must be rendered.

        By default, we return a boolean indicating whether the page has
        suitable child pages to include in such a menu. But, if you are
        overriding the `modify_submenu_items` method to programatically add
        items that aren't child pages, you'll likely need to alter this method
        too, so the template knows there are sub items to be rendered.
        """
        return menu_instance.page_has_children(self)

    def get_repeated_menu_item(
        self, current_page, current_site, apply_active_classes,
        original_menu_tag
    ):
        """Return something that can be used to display a 'repeated' menu item
        for this specific page."""

        menuitem = copy(self)
        setattr(menuitem, 'text', self.repeated_item_text or self.title)
        setattr(menuitem, 'href', self.relative_url(current_site))
        active_class = ''
        if apply_active_classes and self == current_page:
            active_class = app_settings.ACTIVE_CLASS
        setattr(menuitem, 'active_class', active_class)
        return menuitem
