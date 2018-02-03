from distutils.version import LooseVersion

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from . import app_settings

from wagtail import VERSION as WAGTAIL_VERSION
if WAGTAIL_VERSION >= (2, 0):
    from wagtail.admin.edit_handlers import (
        FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel,
        PageChooserPanel, ObjectList, TabbedInterface
    )
else:
    from wagtail.wagtailadmin.edit_handlers import (
        FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel,
        PageChooserPanel, ObjectList, TabbedInterface
    )


# ########################################################
# For menu models
# ########################################################

def _define_inlinepanel(relation_name, **kwargs):
    klass = InlinePanel
    defaults = {'label': _('menu items')}
    if 'condensedinlinepanel' in settings.INSTALLED_APPS:
        import condensedinlinepanel
        from condensedinlinepanel.edit_handlers import CondensedInlinePanel
        if LooseVersion(condensedinlinepanel.__version__) >= LooseVersion('0.3'):
            klass = CondensedInlinePanel
            defaults = {
                'heading': _('Menu items'),
                'label': _("Add new item"),
                'new_card_header_text': _("New item"),
            }
    defaults.update(kwargs)
    return klass(relation_name, **defaults)


def FlatMenuItemsInlinePanel(**kwargs):  # noqa
    """
    Returns either a ``InlinePanel`` or ``CondensedInlinePanel`` instance (
    depending on whether a sufficient version of `condensedinlinepanel` is
    installed) for editing menu items for a flat menu.

    Use in panel definitions like any standard panel class. Any supplied kwargs
    will be passed on as kwargs to the target class's __init__ method.
    """
    return _define_inlinepanel(
        relation_name=app_settings.FLAT_MENU_ITEMS_RELATED_NAME, **kwargs)


def MainMenuItemsInlinePanel(**kwargs):  # noqa
    """
    Returns either a ``InlinePanel`` or ``CondensedInlinePanel`` instance (
    depending on whether a sufficient version of `condensedinlinepanel` is
    installed) for editing menu items for a main menu.

    Use in panel definitions like any standard panel class. Any supplied kwargs
    will be passed on as kwargs to the target class's __init__ method.
    """
    return _define_inlinepanel(
        relation_name=app_settings.MAIN_MENU_ITEMS_RELATED_NAME, **kwargs)


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
        heading=_('Rendering setings'),
        children=(
            FieldPanel('max_levels'),
            FieldPanel('use_specific')
        ),
    ),
)

# ##########################################################
# Deprecated panel layouts (to be removed in v2.8)
# ##########################################################

main_menu_panels = (
    MainMenuItemsInlinePanel(),
    MultiFieldPanel(
        heading=_("Advanced settings"),
        children=(FieldPanel('max_levels'), FieldPanel('use_specific')),
        classname="collapsible collapsed",
    ),
)

flat_menu_panels = (
    MultiFieldPanel(
        heading=_("Settings"),
        children=(
            FieldPanel('title'),
            FieldPanel('site'),
            FieldPanel('handle'),
            FieldPanel('heading'),
        )
    ),
    FlatMenuItemsInlinePanel(),
    MultiFieldPanel(
        heading=_("Advanced settings"),
        children=(FieldPanel('max_levels'), FieldPanel('use_specific')),
        classname="collapsible collapsed",
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
