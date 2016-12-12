from __future__ import absolute_import, unicode_literals

from django import forms
from wagtail.wagtailadmin.forms import WagtailAdminModelForm

from . import app_settings


class FlatMenuAdminForm(WagtailAdminModelForm):
    def __init__(self, *args, **kwargs):
        super(FlatMenuAdminForm, self).__init__(*args, **kwargs)
        if app_settings.FLAT_MENUS_HANDLE_CHOICES:
            self.fields['handle'] = forms.ChoiceField(
                choices=app_settings.FLAT_MENUS_HANDLE_CHOICES)
