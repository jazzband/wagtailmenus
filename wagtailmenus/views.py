from __future__ import absolute_import, unicode_literals

from django import forms
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.utils import quote, unquote

from wagtail.wagtailadmin import messages
from wagtail.wagtailcore.models import Site

from wagtail.contrib.modeladmin.views import WMABaseView, ModelFormView
from .models import MainMenu


class SiteSwitchForm(forms.Form):
    site = forms.ChoiceField(choices=[])

    class Media:
        js = [
            'wagtailmenus/js/site-switcher.js',
        ]

    def __init__(self, current_site, url_helper, **kwargs):
        initial = {'site': url_helper.get_action_url('edit', current_site.pk)}
        super(SiteSwitchForm, self).__init__(initial=initial, **kwargs)
        sites = []
        for site in Site.objects.all():
            sites.append((url_helper.get_action_url('edit', site.pk), site))
        self.fields['site'].choices = sites


class MainMenuIndexView(WMABaseView):

    def dispatch(self, request, *args, **kwargs):
        site = Site.find_for_request(request)
        return redirect(
            self.model_admin.url_helper.get_action_url('edit', site.pk))


class MainMenuEditView(ModelFormView):
    page_title = _('Editing')
    instance_pk = None
    instance = None

    def __init__(self, model_admin, instance_pk):
        super(MainMenuEditView, self).__init__(model_admin)
        self.instance_pk = unquote(instance_pk)
        self.pk_safe = quote(self.instance_pk)
        self.site = get_object_or_404(Site, id=self.instance_pk)
        self.edit_url = self.model_admin.url_helper.get_action_url(
            'edit', self.instance_pk)
        self.instance = MainMenu.get_for_site(self.site)
        self.instance.save()

    def get_meta_title(self):
        return _('Editing %s') % self.opts.verbose_name

    def get_page_subtitle(self):
        return capfirst(self.opts.verbose_name)

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not self.permission_helper.user_can_edit_obj(user, self.instance):
            raise PermissionDenied
        self.site_switcher = None
        if Site.objects.count() > 1:
            url_helper = self.model_admin.url_helper
            self.site_switcher = SiteSwitchForm(self.site, url_helper)
            site_from_get = request.GET.get('site', None)
            if site_from_get and site_from_get != self.instance_pk:
                return redirect(
                    url_helper.get_action_url('edit', site_from_get))
        return super(MainMenuEditView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MainMenuEditView, self).get_context_data(**kwargs)
        context.update({
            'site': self.site,
            'site_switcher': self.site_switcher,
        })
        return context

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request, _("%s updated.") % capfirst(self.model_name)
        )
        return redirect(self.edit_url)

    def get_error_message(self):
        return _("The menu could not be saved due to errors.")

    def get_template_names(self):
        return ['wagtailmenus/mainmenu_edit.html']
