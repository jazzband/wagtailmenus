from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import (FieldPanel, FieldRowPanel, InlinePanel,
                                  MultiFieldPanel, ObjectList,
                                  PageChooserPanel, TabbedInterface)

from wagtailmenus.conf import settings
from wagtail.models import Page

# ########################################################
# For menu models
# ########################################################


class MenuItemInlinePanel(InlinePanel):

    def __init__(self, **kwargs):
        defaults = {
            'heading': _('Menu items'),
            'label': _('menu item'),
            'relation_name': self.get_default_relation_name(),
        }
        for key, val in defaults.items():
            if not kwargs.get(key):
                kwargs[key] = val

        relation_name = kwargs.pop('relation_name')
        return super().__init__(relation_name, **kwargs)


class FlatMenuItemsInlinePanel(MenuItemInlinePanel):

    @classmethod
    def get_default_relation_name(cls):
        return settings.FLAT_MENU_ITEMS_RELATED_NAME


class MainMenuItemsInlinePanel(MenuItemInlinePanel):

    @classmethod
    def get_default_relation_name(cls):
        return settings.MAIN_MENU_ITEMS_RELATED_NAME


main_menu_content_panels = (
    MainMenuItemsInlinePanel(),
)

flat_menu_content_panels = (
    MultiFieldPanel(
        heading=_("Menu details"),
        children=(
            FieldPanel('title'),
            FieldPanel('site'),
            FieldPanel('handle'),
            FieldPanel('heading'),
        ),
        classname="collapsible"
    ),
    FlatMenuItemsInlinePanel(),
)

menu_settings_panels = (
    MultiFieldPanel(
        heading=_('Render settings'),
        children=(
            FieldPanel('max_levels'),
        ),
    ),
)


# ########################################################
# For AbstractLinkPage
# ########################################################

linkpage_panels = [
    MultiFieldPanel([
        FieldPanel('title', classname="title"),
        PageChooserPanel('link_page'),
        FieldPanel('link_url'),
        FieldPanel('url_append'),
        FieldPanel('extra_classes'),
    ])
]

linkpage_tab = ObjectList(
    linkpage_panels, heading=_("Settings"), classname="settings"
)

linkpage_edit_handler = TabbedInterface([linkpage_tab])


# ########################################################
# For MenuPageMixin and MenuPage
# ########################################################

menupage_panel = MultiFieldPanel(
    heading=_("Advanced menu behaviour"),
    classname="collapsible collapsed",
    children=(
        FieldPanel('repeat_in_subnav'),
        FieldPanel('repeated_item_text'),
    )
)

menupage_settings_panels = Page.settings_panels + [menupage_panel]
