from django.utils.translation import ugettext_lazy as _
from wagtailmodeladmin.options import (
    ModelAdmin, ModelAdminGroup, wagtailmodeladmin_register)
from .models import MainMenu, FlatMenu


class MainMenuAdmin(ModelAdmin):
    model = MainMenu
    menu_label = _('Main navigation')
    menu_icon = 'link'
    list_filter = ('site', )
    add_to_settings_menu = True


class FlatMenuAdmin(ModelAdmin):
    model = FlatMenu
    menu_icon = 'list-ol'
    list_display = ('title', 'handle', )
    list_filter = ('site', )
    add_to_settings_menu = True

wagtailmodeladmin_register(MainMenuAdmin)
wagtailmodeladmin_register(FlatMenuAdmin)
