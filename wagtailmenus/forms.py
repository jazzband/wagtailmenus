from django import forms
from django.utils.translation import gettext_lazy as _
from wagtail.admin.forms import WagtailAdminModelForm, WagtailAdminPageForm

from wagtailmenus.conf import settings


class FlatMenuAdminForm(WagtailAdminModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if settings.FLAT_MENUS_HANDLE_CHOICES:
            self.fields['handle'] = forms.ChoiceField(
                label=self.fields['handle'].label,
                choices=settings.FLAT_MENUS_HANDLE_CHOICES
            )


class LinkPageAdminForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].help_text = _(
            "By default, this will be used as the link text when appearing "
            "in menus."
        )
