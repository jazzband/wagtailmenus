from __future__ import absolute_import, unicode_literals

from django import forms
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.contrib.admin.utils import quote, unquote

from wagtail.wagtailadmin import messages
from wagtail.wagtailcore.models import Site

from wagtailmodeladmin.views import WMABaseView, WMAFormView
from wagtailmodeladmin.helpers import get_url_name
from .models import MainMenu

edit_url_name = get_url_name(MainMenu._meta, 'edit')


class SiteSwitchForm(forms.Form):
    site = forms.ChoiceField(choices=[])

    class Media:
        js = [
            'wagtailmenus/js/site-switcher.js',
        ]

    def __init__(self, current_site, **kwargs):
        initial_data = {'site': self.get_change_url(current_site)}
        super(SiteSwitchForm, self).__init__(initial=initial_data, **kwargs)
        sites = [(self.get_change_url(site), site)
                 for site in Site.objects.all()]
        self.fields['site'].choices = sites

    @classmethod
    def get_change_url(cls, site):
        return reverse(edit_url_name, args=[site.pk])


class MainMenuIndexView(WMABaseView):

    def dispatch(self, request, *args, **kwargs):
        if not self.permission_helper.has_list_permission(request.user):
            raise PermissionDenied
        site = Site.find_for_request(request)
        return redirect(self.get_edit_url(site))


class MainMenuEditView(WMAFormView):
    page_title = _('Editing')
    object_id = None
    instance = None

    def __init__(self, model_admin, object_id):
        super(MainMenuEditView, self).__init__(model_admin)
        self.object_id = unquote(object_id)
        self.pk_safe = quote(self.object_id)
        self.site = get_object_or_404(Site, id=self.object_id)
        self.edit_url = reverse(edit_url_name, args=[self.object_id])
        self.instance = MainMenu.for_site(self.site)
        self.instance.save()

    def get_meta_title(self):
        return _('Editing %s') % self.opts.verbose_name

    def get_page_subtitle(self):
        return capfirst(self.opts.verbose_name)

    def check_action_permitted(self, user):
        return self.permission_helper.can_edit_object(user, self.instance)

    def dispatch(self, request, *args, **kwargs):
        self.site_switcher = None
        if Site.objects.count() > 1:
            self.site_switcher = SiteSwitchForm(self.site)
            if request.GET.get('site', None):
                return redirect(request.GET['site'])
        return super(MainMenuEditView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MainMenuEditView, self).get_context_data(**kwargs)
        context.update({
            'site': self.site,
            'site_switcher': self.site_switcher,
        })
        return context

    def form_valid(self, form):
        instance = form.save()
        messages.success(
            self.request, _("%s updated.") % capfirst(self.model_name)
        )
        return redirect(self.edit_url)

    def get_error_message(self):
        return _("The %s could not be saved due to errors.") % self.model_name

    def get_template_names(self):
        return ['wagtailmenus/mainmenu_edit.html']
