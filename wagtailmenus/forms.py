from django import forms
from django.utils.translation import ugettext_lazy as _
from wagtail import VERSION as WAGTAIL_VERSION
if WAGTAIL_VERSION >= (2, 0):
    from wagtail.admin.forms import WagtailAdminModelForm, WagtailAdminPageForm
else:
    from wagtail.wagtailadmin.forms import WagtailAdminModelForm, WagtailAdminPageForm

from . import app_settings


class FlatMenuAdminForm(WagtailAdminModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if app_settings.FLAT_MENUS_HANDLE_CHOICES:
            self.fields['handle'] = forms.ChoiceField(
                label=self.fields['handle'].label,
                choices=app_settings.FLAT_MENUS_HANDLE_CHOICES
            )


class LinkPageAdminForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].help_text = _(
            "By default, this will be used as the link text when appearing "
            "in menus."
        )
