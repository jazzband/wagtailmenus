from django.contrib.admin.utils import quote
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from wagtail.admin.widgets.button import ListingButton
from wagtail.snippets.views.snippets import CreateView, IndexView, SnippetViewSet

"""
Extension to SnippetViewSet which enables Snippet copying
Can be removed once Wagtail supports this function natively,
with some small refactoring in FlatMenuAdmin.
"""

class CopyView(CreateView):
    view_name = "copy"
    template_name = "wagtailsnippets/snippets/create.html"
    error_message = _("The snippet could not be copied due to errors.")

    def run_before_hook(self):
        return self.run_hook("before_copy_snippet", self.request, self.model)

    def run_after_hook(self):
        return self.run_hook("after_copy_snippet", self.request, self.object)

    def _get_initial_form_instance(self):
        return self.get_object()
    

class CopyableSnippetIndexView(IndexView):
    copy_url_name = None

    def get_copy_url(self, instance):
        return reverse(self.copy_url_name, args=(quote(instance.pk),))
    
    def get_list_more_buttons(self, instance):
        r = super().get_list_more_buttons(instance)
        r.append(ListingButton(
            _("Copy"),
            url=self.get_copy_url(instance),
            icon_name="copy",
            attrs={ "aria-label": _("Copy '%(title)s'") % {"title": str(instance)} },
            priority=15,
        ))
        return r


class CopyableSnippetViewSet(SnippetViewSet):
    #: The view class to use for the copy view; must be a subclass of ``wagtail.snippet.views.snippets.CopyView``.
    copy_view_class = CopyView

    #: The template to use for the edit view.
    copy_template_name = ""

    @property
    def copy_view(self):
        return self.copy_view_class.as_view(
            model=self.model,
            template_name=self.get_copy_template(),
            header_icon=self.icon,
            permission_policy=self.permission_policy,
            panel=self._edit_handler,
            form_class=self.get_form_class(),
            index_url_name=self.get_url_name("list"),
            add_url_name=self.get_url_name("add"),
            edit_url_name=self.get_url_name("edit"),
            preview_url_name=self.get_url_name("preview_on_add"),
        )

    def get_common_view_kwargs(self, **kwargs):
        view_kwargs = super().get_common_view_kwargs(**kwargs)
        view_kwargs["copy_url_name"] = self.get_url_name("copy")
        return view_kwargs

    def get_copy_template(self):
        return self.copy_template_name or self.get_templates("copy")
    
    def get_urlpatterns(self):
        urls = super().get_urlpatterns()

        return urls + [
            path("copy/<str:pk>/", self.copy_view, name="copy")
        ]
