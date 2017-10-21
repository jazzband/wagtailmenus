from __future__ import absolute_import, unicode_literals
from distutils.version import LooseVersion

from django.conf import settings
from django.utils.functional import SimpleLazyObject
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, PageChooserPanel,
    ObjectList, TabbedInterface)

from . import app_settings


# ########################################################
# For menu models
# ########################################################
def _define_inlinepanel(relation_name, **kwargs):
    klass = InlinePanel
    panel_kwargs = dict(
        label=_('menu items')
    )
    if 'condensedinlinepanel' in settings.INSTALLED_APPS:
        import condensedinlinepanel
        from condensedinlinepanel.edit_handlers import CondensedInlinePanel
        if LooseVersion(condensedinlinepanel.__version__) >= LooseVersion('0.3'):
            klass = CondensedInlinePanel
            panel_kwargs = dict(
                heading=_('Menu items'),
                label=("Add new item"),
                new_card_header_text=_("New item"),
            )
    panel_kwargs.update(kwargs)
    return klass(relation_name, **panel_kwargs)


def FlatMenuItemsInlinePanel(**kwargs):  # noqa
    """
    If ``collapsedinlinepanel`` is installed a `CondensedInlinePanel` will be
    used, otherwise Wagtail's built-in `InlinePanel` will be used.
    Use in panel definitions like so:

    panels = [
        FieldPanel('title'),
        FlatMenuItemsInlinePanel(),
    ]
    """
    return _define_inlinepanel(
        rel_name=app_settings.FLAT_MENU_ITEMS_RELATED_NAME, **kwargs)


def MainMenuItemsInlinePanel(**kwargs):  # noqa
    """
    Returns a ``InlinePanel`` instance for editing menu items for a main menu.
    If ``collapsedinlinepanel`` is installed a ``CondensedInlinePanel``
    instance will be returned instead. Use in panel definitions like so:

    panels = [
        FieldPanel('title'),
        MainMenuItemsInlinePanel(),
    ]
    """
    return _define_inlinepanel(
        rel_name=app_settings.MAIN_MENU_ITEMS_RELATED_NAME, **kwargs)


main_menu_content_panels = [
    SimpleLazyObject(MainMenuItemsInlinePanel),
]

flat_menu_content_panels = [
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
    SimpleLazyObject(FlatMenuItemsInlinePanel),
]

menu_settings_panels = [
    MultiFieldPanel(
        heading=_('Rendering setings'),
        children=(
            FieldPanel('max_levels'),
            FieldPanel('use_specific')
        ),
        classname="collapsible"
    ),
]


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
