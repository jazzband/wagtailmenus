from distutils.version import LooseVersion

from django.conf import settings as django_settings
from django.utils.translation import gettext_lazy as _
from wagtailmenus.conf import settings
try:
    from wagtail.admin.panels import (
        FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel,
        PageChooserPanel, ObjectList, TabbedInterface
    )
except ImportError:
    from wagtail.admin.edit_handlers import (
        FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel,
        PageChooserPanel, ObjectList, TabbedInterface
    )


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
# For MenuPageMixin
# ########################################################

menupage_panel = MultiFieldPanel(
    heading=_("Advanced menu behaviour"),
    classname="collapsible collapsed",
    children=(
        FieldPanel('repeat_in_subnav'),
        FieldPanel('repeated_item_text'),
    )
)

menupage_settings_panels = [
    MultiFieldPanel(
        heading=_("Scheduled publishing"),
        classname="publishing",
        children=(
            FieldRowPanel((
                FieldPanel('go_live_at', classname="col6"),
                FieldPanel('expire_at', classname="col6"),
            )),
        )
    ),
    menupage_panel,
]

menupage_settings_tab = ObjectList(
    menupage_settings_panels, heading=_("Settings"), classname="settings"
)
