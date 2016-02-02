from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, FieldRowPanel, MultiFieldPanel, ObjectList)
from django.utils.translation import ugettext_lazy as _


"""
`settings_panels` arrangement, including new menu-related fields from the
MenuPage abstract class.
"""
menupage_settings_panels = (
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
    MultiFieldPanel(
        heading=_("Advanced menu behaviour"),
        classname="collapsible collapsed",
        children=(
            FieldPanel('repeat_in_subnav'),
            FieldPanel('subnav_menu_text'),
        )
    )
)

"""
The above `settings_panels` arrangement configured as tab, for easier
integration into custom edit_handlers.
"""
menupage_settings_tab = ObjectList(
    menupage_settings_panels, heading=_("Settings"), classname="settings")
