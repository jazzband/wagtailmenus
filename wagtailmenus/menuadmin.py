from django.contrib.admin.utils import unquote, quote
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import TabbedInterface, ObjectList
from wagtail.models import Site
from wagtail.snippets.views.snippets import CreateView, EditView, IndexView, SnippetViewSet

from wagtailmenus import panels
from wagtailmenus.conf import settings
from wagtailmenus.forms import SiteSwitchForm

# Wagtail 6 introduced Snippet copy.
# CopyableSnippetViewSet provides the equivalent in Wagtail 5.2
from wagtail import VERSION as WAGTAIL_VERSION
if WAGTAIL_VERSION >= (6, 0):
    CopyableSnippetIndexView = IndexView
    CopyableSnippetViewSet = SnippetViewSet
else:
    from .copyable_snippetviewset import CopyableSnippetIndexView, CopyableSnippetViewSet


class MainMenuIndexView(IndexView):
    def dispatch(self, request, *args, **kwargs):
        site = Site.find_for_request(request)
        return redirect(self.get_edit_url(site))


class MainMenuEditView(EditView):
    def setup(self, request, *args, **kwargs):
        self.site = get_object_or_404(Site, id=unquote(kwargs['pk']))

        super().setup(request, *args, **kwargs)

        self.site_switcher = None
        if Site.objects.count() > 1:
            self.site_switcher = SiteSwitchForm(self.site, self.edit_url_name)
            
    def get_object(self, queryset=None):
        self.object = self.model.get_for_site(self.site)
        self.object.save()
        self.live_object = self.object
        return self.object
    
    def get_edit_url(self):
        return reverse(self.edit_url_name, args=(quote(self.site.pk),))

    @property
    def media(self):
        if self.site_switcher:
            return self.site_switcher.media
        return []

    def dispatch(self, request, *args, **kwargs):
        self.site_switcher = None
        if Site.objects.count() > 1:
            self.site_switcher = SiteSwitchForm(self.site, self.edit_url_name)
            site_from_get = request.GET.get('site', None)
            if site_from_get and site_from_get != str(self.site.pk):
                return redirect(reverse(self.edit_url_name, args=(quote(site_from_get),)))

        return super().dispatch(request, *args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'action_url': "?",
            'site': self.site,
            'site_switcher': self.site_switcher,
        })
        return context
    
    def form_valid(self, form):
        super().form_valid(form)
        return redirect(self.get_edit_url())


class MainMenuAdmin(SnippetViewSet):
    model = settings.models.MAIN_MENU_MODEL
    menu_label = _('Main menu')
    icon = settings.MAINMENU_MENU_ICON
    url_prefix = "wagtailmenus/mainmenu"
    add_to_settings_menu = True

    index_view_class = MainMenuIndexView

    edit_view_class = MainMenuEditView
    edit_template_name = "wagtailmenus/mainmenu_edit.html"
    if WAGTAIL_VERSION < (6, 3):
        edit_template_name = "wagtailmenus/wagtail_before_63/mainmenu_edit.html"
    error_message = _("The menu could not be saved due to errors.")

    copy_view_enabled = False

    edit_handler = TabbedInterface([
        ObjectList(panels.main_menu_content_panels, heading=_("Content")),
        ObjectList(panels.menu_settings_panels, heading=_("Settings"),
                    classname="settings"),
    ])


class FlatMenuIndexView(CopyableSnippetIndexView):
    @property
    def list_display(self):
        if self.is_multisite_listing:
            return ('title', 'handle_formatted', 'site', 'items')
        return ('title', 'handle_formatted', 'items')

    @list_display.setter
    def list_display(self, _):
        pass

    @property
    def list_filter(self):
        if self.is_multisite_listing:
            return ('site', 'handle')
        return ()

    @list_filter.setter
    def list_filter(self, _):
        pass

    @cached_property
    def is_multisite_listing(self):
        return self.get_base_queryset().values('site').distinct().count() > 1


class FlatMenuCreateView(CreateView):
    error_message = _("The flat menu could not be saved due to errors")


class FlatMenuAdmin(CopyableSnippetViewSet):
    model = settings.models.FLAT_MENU_MODEL
    menu_label = _('Flat menus')
    icon = settings.FLATMENU_MENU_ICON
    url_prefix = "wagtailmenus/flatmenu"
    add_to_settings_menu = True

    index_view_class = FlatMenuIndexView
    index_template_name = "wagtailmenus/flatmenu_index.html"
    list_display = ('title', 'handle_formatted', 'site', 'items')
    list_filter = ('site', 'handle')
    ordering = ('-site__is_default_site', 'site__hostname', 'handle')

    add_view_class = FlatMenuCreateView
    error_message = _("The flat menu could not be saved due to errors.")

    edit_handler = TabbedInterface([
        ObjectList(panels.flat_menu_content_panels, heading=_("Content")),
        ObjectList(panels.menu_settings_panels, heading=_("Settings"),
                    classname="settings"),
    ])
