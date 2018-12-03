from django import forms
from django.conf import settings as django_settings
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.template import loader
from wagtail.core.models import Page, Site

from wagtailmenus.conf import settings
from wagtailmenus.utils.misc import make_dummy_request
from . import form_fields as fields


UNDERIVABLE_MSG = _(
    "This value was not provided and could not be derived from other values."
)


class BaseAPIViewArgumentForm(forms.Form):
    """
    A form class that accepts 'view' and 'request' arguments at initialisation,
    is capable of rendering itself to a template (in a similar fashion to
    ``django_filters.rest_framework.DjangoFilterBackend``), and has some
    custom cleaning behaviour to better handle missing values.
    """
    def __init__(self, view, request, **kwargs):
        self._view = view
        self._request = request
        super().__init__(**kwargs)

    def full_clean(self):
        """
        Because non-required arguments are often not provided for API requests,
        and because request values are not 'posted' by the form, initial data
        misses it's usual opportunity to become a default value. This override
        changes that by supplementing ``self.data`` with initial values before
        the usual cleaning happens.
        """
        self.supplement_missing_data_with_initial_values()
        return super().full_clean()

    def supplement_missing_data_with_initial_values(self):
        supplementary_vals = {}
        for name, field in self.fields.items():
            if not field.required and self.data.get(name) in ('', None):
                val = self.get_initial_for_field(field, name)
                if val is not None:
                    supplementary_vals[name] = val

        if supplementary_vals:
            if not getattr(self.data, '_mutable', True):
                self.data = self.data.copy()
            self.data.update(supplementary_vals)
        return self.data

    @property
    def template_name(self):
        if 'crispy_forms' in django_settings.INSTALLED_APPS:
            return 'wagtailmenus/api/forms/crispy_form.html'
        return 'wagtailmenus/api/forms/form.html'

    def to_html(self, request):
        template = loader.get_template(self.template_name)
        context = {'form': self}
        return template.render(context, request)

    @property
    def helper(self):
        if 'crispy_forms' not in django_settings.INSTALLED_APPS:
            return

        from crispy_forms.helper import FormHelper
        from crispy_forms.layout import Layout, Submit

        layout_components = list(self.fields.keys()) + [
            Submit('', _('Submit'), css_class='btn-default'),
        ]
        obj = FormHelper()
        obj.form_method = 'GET'
        obj.template_pack = 'bootstrap3'
        obj.layout = Layout(*layout_components)
        return obj


class BaseMenuGeneratorArgumentForm(BaseAPIViewArgumentForm):
    site = fields.SiteChoiceField(
        label=_('Site'),
        help_text=_(
            "The ID of the Wagtail Site you are generating the menu for."
        ),
    )
    current_url = forms.URLField(
        required=False,
        label=_("Current URL"),
        help_text=_(
            "The URL you are generating the menu for (relative to the site "
            "root). If you are generating a menu for a URL that does not map "
            "exactly to a Page object, you can provide this in place of "
            "'current_page' to help derive active classes and other values."
        ),
    )
    current_page = fields.PageChoiceField(
        label=_('Current page'),
        required=False,
        help_text=_(
            "The ID of the Wagtail Page you are generating the menu for."
        ),
    )
    max_levels = fields.MaxLevelsChoiceField(
        label=_('Maximum levels'),
        required=False,
        help_text=_(
            "The maximum number of levels of menu items that should be "
            "included in the result. Defaults to the relevant setting value "
            "for this menu type."
        )
    )
    use_specific = fields.UseSpecificChoiceField(
        label=_('Specific page usage'),
        required=False,
        help_text=_(
            "How 'specific' page objects should be utilised when generating "
            "the result. Defaults to the relevant setting value for this menu "
            "type."
        )
    )
    apply_active_classes = fields.BooleanChoiceField(
        label=_('Apply active classes'),
        required=False,
        help_text=_(
            "Whether the view should set 'active_class' attributes on menu "
            "items to help indicate a user's current position within the menu "
            "structure. Defaults to the relevant setting value for this menu "
            "type."
        ),
    )
    allow_repeating_parents = fields.BooleanChoiceField(
        label=_('Allow repeating parents'),
        required=False,
        help_text=_(
            "Whether the view should allow pages inheriting from MenuPage or "
            "MenuPageMixin to add duplicates of themselves to their "
            "'children' when appearing as menu items. Defaults to the "
            "relevant setting value for this menu type."
        )
    )
    use_absolute_page_urls = fields.BooleanChoiceField(
        label=_('Use absolute page URLs'),
        required=False,
        help_text=_(
            "Whether the view should use absolute page URLs instead of "
            "relative ones for menu items that link to pages, even if the "
            "page is within the page tree for the provided 'site'. Defaults "
            "to the relevant setting value for this menu type."
        )
    )
    language = forms.ChoiceField(
        label=_('Language'),
        required=False,
        choices=django_settings.LANGUAGES,
        initial=django_settings.LANGUAGE_CODE,
        help_text=_(
            "The language you wish to rendering the menu in. Must be one of "
            "the languages defined in your LANGUAGES setting. Will only "
            "affect the result if USE_I18N is True. Defaults to LANGUAGE_CODE."
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['current_page'].queryset = Page.objects.filter(depth__gt=1)
        self.fields['site'].queryset = Site.objects.all()
        if not django_settings.USE_I18N:
            self.fields['language'].widget = forms.HiddenInput()
        self._dummy_request = None

    def clean(self):
        cleaned_data = super().clean()
        self.derive_current_page(cleaned_data)
        self.derive_ancestor_page_ids(cleaned_data)
        return cleaned_data

    def make_dummy_request(self, url):
        if not url:
            return
        return make_dummy_request(url=url, original_request=self._request)

    def derive_current_page(self, cleaned_data, force_derivation=False, accept_best_match=True):
        """
        If necessary, attempts to derive a 'current_page' value from other
        values in ``cleaned_data``, and adds that value to ``cleaned_data``.
        By default, the page is only derived when 'apply_active_classes' is
        True. But, ``force_derivation`` can be used to force it.

        If the URL doesn't match a Page 'exactly' and `accept_best_match` is
        True, ``guess_page_from_url()`` will attempt to find a 'best match' by
        removing components from the url. If such a match is found, it will be
        added to ``cleaned_data`` as 'best_match_page'.
        """
        if(
            cleaned_data.get('current_page') or
            not cleaned_data.get('site') or
            not cleaned_data.get('current_url') or (
                not force_derivation and
                not cleaned_data.get('apply_active_classes')
            )
        ):
            return

        match, is_exact_match = self.guess_page_from_url(
            url=cleaned_data['url'],
            site=cleaned_data['site'],
            accept_best_match=accept_best_match,
        )

        if match:
            if is_exact_match:
                cleaned_data['current_page'] = match
            else:
                cleaned_data['best_match_page'] = match

        if not accept_best_match and not cleaned_data['current_page']:
            self.add_error('current_page', UNDERIVABLE_MSG)

    def guess_page_from_url(self, site, url, accept_best_match=True):
        """
        Attempts to guess a wagtail Page from a URL. Returns a tuple, where
        the first element is the matching Page object (or None if no match
        was found), and a boolean indicating whether the page matched the
        URL exactly.

        If ``accept_best_match`` is True, and a matching page isn't found on
        the first attempt, the method will recursively remove components from
        the url and retry until a match is found.
        """
        request = self.make_dummy_request(url)
        first_run = True
        match = None
        path_components = [pc for pc in request.path.split('/') if pc]
        while match is None and path_components:
            try:
                match = site.root_page.specific.route(request, path_components)[0]
                if first_run:
                    return match, True
                else:
                    return match, False
            except Http404:
                if not accept_best_match:
                    break
                path_components.pop()
                first_run = False
        return None, False

    def derive_ancestor_page_ids(self, cleaned_data):
        """
        If required, attempts to derive a set of 'ancestor_page_ids' from
        page values in ``cleaned_data`` and add them to ``cleaned_data``.
        """
        source_page = cleaned_data.get('current_page') or cleaned_data.get('best_match_page')
        if source_page and cleaned_data.get('apply_active_classes'):
            ancestor_ids = set(
                source_page.get_ancestors(inclusive=cleaned_data.get('current_page') is None)
                .filter(depth__gte=settings.SECTION_ROOT_DEPTH)
                .values_list('id', flat=True)
            )
        else:
            ancestor_ids = ()
        cleaned_data['ancestor_page_ids'] = ancestor_ids


class BaseMenuModelGeneratorArgumentForm(BaseMenuGeneratorArgumentForm):
    max_levels = fields.MaxLevelsChoiceField(
        label=_('Maximum levels'),
        required=False,
        empty_label=_('Default: Use the value set for the menu object'),
        help_text=_(
            "The maximum number of levels of menu items that should be "
            "included in the result. Defaults to the 'max_levels' field value "
            "on the matching menu object."
        ),
    )
    use_specific = fields.UseSpecificChoiceField(
        label=_('Specific page usage'),
        required=False,
        empty_label=_('Default: Use the value set for the menu object'),
        help_text=_(
            "How 'specific' page objects should be utilised when generating "
            "the result. Defaults to the 'use_specific' field value on the "
            "matching menu object."
        ),
    )


class MainMenuGeneratorArgumentForm(BaseMenuModelGeneratorArgumentForm):
    site = fields.SiteChoiceField(
        label=_('Site'),
        help_text=_(
            "The ID of the Wagtail Site you are generating a menu for. Used "
            "to retrieve the relevant menu object from the database."
        ),
    )

    field_order = (
        'site',
        'current_page',
        'current_url',
        'max_levels',
        'use_specific',
        'apply_active_classes',
        'allow_repeating_parents',
        'use_absolute_page_urls',
        'language',
    )


class FlatMenuGeneratorArgumentForm(BaseMenuModelGeneratorArgumentForm):
    handle = fields.FlatMenuHandleField(
        label=_('Handle'),
        help_text=_(
            "The 'handle' for the flat menu you wish to generate. For "
            "example: 'info' or 'contact'."
        )
    )
    fall_back_to_default_site_menus = fields.BooleanChoiceField(
        label=_('Fall back to default site menus'),
        required=False,
        help_text=_(
            "If a menu cannot be found matching the provided 'handle' for the "
            "supplied (or derived) site, use the flat menu defined for the "
            "'default' site (if available)."
        )
    )

    field_order = (
        'site',
        'handle',
        'fall_back_to_default_site_menus',
        'current_page',
        'current_url',
        'max_levels',
        'use_specific',
        'apply_active_classes',
        'allow_repeating_parents',
        'use_absolute_page_urls',
        'language',
    )


class ChildrenMenuGeneratorArgumentForm(BaseMenuGeneratorArgumentForm):
    parent_page = fields.PageChoiceField(
        label=_("Parent page"),
        required=False,
        help_text=_(
            "The page you wish to show children page links for (if different "
            "to 'current_page')."
        )
    )

    field_order = (
        'site',
        'current_page',
        'current_url',
        'parent_page',
        'max_levels',
        'use_specific',
        'apply_active_classes',
        'allow_repeating_parents',
        'use_absolute_page_urls',
        'language',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent_page'].queryset = Page.objects.filter(depth__gt=1)

    def clean(self):
        cleaned_data = super().clean()
        self.derive_parent_page(cleaned_data)
        return cleaned_data

    def derive_parent_page(self, cleaned_data):
        """
        If necessary, and 'current_page' has been provided or successfully
        derived, add the same value to ``cleaned_data`` as 'parent_page'.
        """
        if cleaned_data.get('parent_page'):
            return

        if cleaned_data.get('current_page'):
            cleaned_data['parent_page'] = cleaned_data['current_page']
        else:
            self.add_error('parent_page', UNDERIVABLE_MSG)

    def derive_current_page(self, cleaned_data, force_derivation=False, accept_best_match=False):
        """
        Overrides ArgValidatorForm.derive_current_page(),
        because if neither 'parent_page' or 'current_page' have been
        provided, we want to force derivation of 'current_page', so that it
        can serve as a stand-in for 'parent_page'.

        A 'best match' is not a good enough stand-in for 'parent_page', so we
        use a False value for 'accept_best_match' by default.
        """
        force_derivation = force_derivation or (
            not cleaned_data.get('parent_page') and
            not cleaned_data.get('current_page')
        )
        super().derive_current_page(cleaned_data, force_derivation, accept_best_match)


class SectionMenuGeneratorArgumentForm(BaseMenuGeneratorArgumentForm):
    section_root_page = fields.PageChoiceField(
        label=_("Section root page"),
        required=False,
        help_text=_(
            "The root page for the 'section', whose children and other "
            "decendents you want show menu items for. If not supplied, the "
            "view will attempt to derive this from 'current_page' or "
            "'current_url'."
        )
    )

    field_order = (
        'site',
        'current_page',
        'current_url',
        'section_root_page',
        'max_levels',
        'use_specific',
        'apply_active_classes',
        'allow_repeating_parents',
        'use_absolute_page_urls',
        'language',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['section_root_page'].queryset = Page.objects.filter(
            depth__exact=settings.SECTION_ROOT_DEPTH)

    def clean(self):
        """
        Allow 'section_root_page' to be derived from other values if it was not
        provided.
        """
        cleaned_data = super().clean()
        self.derive_section_root_page(cleaned_data)
        return cleaned_data

    def derive_section_root_page(self, cleaned_data):
        """
        If not already present, attempt to derive a 'section_root_page' value
        from page values in ``cleaned_data`` update supplied ``data`` dictionary to include it.
        """
        if cleaned_data.get('section_root_page'):
            return

        source_page = cleaned_data.get('current_page') or cleaned_data.get('best_match_page')
        section_root_depth = settings.SECTION_ROOT_DEPTH
        if source_page is None or source_page.depth < section_root_depth:
            self.add_error('section_root_page', UNDERIVABLE_MSG)
            return
        if source_page.depth > section_root_depth:
            cleaned_data['section_root_page'] = source_page.get_ancestors().get(
                depth__exact=section_root_depth)
        else:
            cleaned_data['section_root_page'] = source_page

    def derive_current_page(self, cleaned_data, force_derivation=False, accept_best_match=True):
        """
        Overrides ArgValidatorForm.derive_current_page(),
        because if neither 'section_root_page' or 'current_page' have been
        provided, we want to force derivation of 'current_page', so that we
        are able to derive 'section_root_page' from it.

        A 'best match' might be good enough to derive 'section_root_page', so
        we'll leave 'accept_best_match' as True by default.
        """
        force_derivation = force_derivation or (
            not cleaned_data.get('section_root_page') and
            not cleaned_data.get('current_page')
        )
        super().derive_current_page(cleaned_data, force_derivation, accept_best_match)
