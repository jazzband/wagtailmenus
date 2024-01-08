from django import forms
from django.contrib.admin.utils import quote
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from wagtail.admin.forms import WagtailAdminModelForm, WagtailAdminPageForm
from wagtail.models import Site

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


class SiteSwitchForm(forms.Form):
    site = forms.ChoiceField(choices=[])

    class Media:
        js = [
            'wagtailmenus/js/site-switcher.js',
        ]

    def __init__(self, current_site, edit_url_name, **kwargs):
        initial = {'site': reverse(edit_url_name, args=(quote(current_site.pk),))}
        super().__init__(initial=initial, **kwargs)
        sites = []
        for site in Site.objects.all():
            sites.append((reverse(edit_url_name, args=(quote(site.pk),)), site))
        self.fields['site'].choices = sites
