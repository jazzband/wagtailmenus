from django.db import models
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, MultiFieldPanel, PublishingPanel
)
from wagtail.wagtailcore.models import Page

from wagtailmenus.models import MenuPage
from .utils import TranslatedField


class MultilingualMenuPage(MenuPage):
    title_de = models.CharField(
        verbose_name=_('title (de)'),
        blank=True,
        max_length=255,
    )
    title_fr = models.CharField(
        verbose_name=_('title (fr)'),
        blank=True,
        max_length=255,
    )
    repeated_item_text_de = models.CharField(
        verbose_name=_('repeated item link text (de)'),
        blank=True,
        max_length=255,
    )
    repeated_item_text_fr = models.CharField(
        verbose_name=_('repeated item link text (fr)'),
        blank=True,
        max_length=255,
    )
    translated_title = TranslatedField(
        'title', 'title_de', 'title_fr'
    )
    translated_repeated_item_text = TranslatedField(
        'repeated_item_text', 'repeated_item_text_de', 'repeated_item_text_fr',
    )

    class Meta:
        abstract = True

    def get_repeated_menu_item(
        self, current_page, current_site, apply_active_classes,
        original_menu_tag
    ):
        item = super(MultilingualMenuPage, self).get_repeated_menu_item(
            current_page, current_site, apply_active_classes, original_menu_tag
        )
        item.text = self.translated_repeated_item_text or self.translated_title
        return item

    settings_panels = [
        PublishingPanel(),
        MultiFieldPanel(
            heading=_("Advanced menu behaviour"),
            classname="collapsible collapsed",
            children=(
                FieldPanel('repeat_in_subnav'),
                FieldPanel('repeated_item_text'),
                FieldPanel('repeated_item_text_de'),
                FieldPanel('repeated_item_text_fr'),
            )
        )
    ]


class HomePage(MenuPage):
    template = 'homepage.html'
    parent_page_types = [Page]


class TopLevelPage(MultilingualMenuPage):
    extra_menuitem_css_class = 'top-level'
    template = 'page.html'
    parent_page_types = [HomePage]


class LowLevelPage(Page):
    extra_menuitem_css_class = 'low-level'
    template = 'page.html'


class TypicalPage(Page):
    template = 'typical-page.html'


class ContactPage(MenuPage):
    template = 'page.html'
    parent_page_types = [HomePage]
    subpage_types = []

    def modify_submenu_items(self, menu_items, current_page,
                             current_ancestor_ids, current_site,
                             allow_repeating_parents, apply_active_classes,
                             original_menu_tag, menu_instance=None):
        menu_items = super(ContactPage, self).modify_submenu_items(
            menu_items, current_page, current_ancestor_ids, current_site,
            allow_repeating_parents, apply_active_classes, original_menu_tag,
            menu_instance)
        """
        If rendering a 'main_menu', add some additional menu items to the end
        of the list that link to various anchored sections on the same page
        """
        if original_menu_tag == 'main_menu':
            base_url = self.relative_url(current_site)
            menu_items.extend((
                {
                    'text': 'Get support',
                    'href': base_url + '#support',
                    'active_class': 'support',
                },
                {
                    'text': 'Speak to someone',
                    'href': base_url + '#call',
                    'active_class': 'call',
                },
                {
                    'text': 'Map & directions',
                    'href': base_url + '#map',
                    'active_class': 'map',
                },
            ))
        return menu_items

    def has_submenu_items(self, current_page, allow_repeating_parents,
                          original_menu_tag, menu_instance=None):
        """
        Because `modify_submenu_items` is being used to add additional menu
        items, we need to indicate in menu templates that `ContactPage` objects
        do have submenu items in main menus, even if they don't have children
        pages.
        """
        if original_menu_tag == 'main_menu':
            return True
        return super(ContactPage, self).has_submenu_items(
            current_page, allow_repeating_parents, original_menu_tag,
            menu_instance)
