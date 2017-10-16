from __future__ import absolute_import, unicode_literals
from distutils.version import LooseVersion

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, PageChooserPanel,
    ObjectList, TabbedInterface)

from . import app_settings


# ########################################################
# For menu models
# ########################################################
inlinepanel_class = InlinePanel
inlinepanel_kwargs = dict(label=_('menu items'))
if app_settings.ADMIN_USE_CONDENSEDINLINEPANEL:
    import condensedinlinepanel
    if LooseVersion(condensedinlinepanel.__version__) >= LooseVersion('0.3'):
        from condensedinlinepanel.edit_handlers import CondensedInlinePanel
        inlinepanel_class = CondensedInlinePanel
        inlinepanel_kwargs = dict(
            heading=_('Menu items'),
            label=("Add new item"),
            new_card_header_text=_("New item"),
        )


main_menu_content_panels = [
    inlinepanel_class(
        app_settings.MAIN_MENU_ITEMS_RELATED_NAME,
        **inlinepanel_kwargs
    )
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
    inlinepanel_class(
        app_settings.FLAT_MENU_ITEMS_RELATED_NAME,
        **inlinepanel_kwargs
    ),
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
