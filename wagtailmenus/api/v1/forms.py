from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.template import loader
from wagtail.core.models import Page, Site

from wagtailmenus.conf import settings as wagtailmenus_settings
from wagtailmenus.api.v1.conf import settings as api_settings
from wagtailmenus.api import form_fields as api_form_fields
from wagtailmenus.utils.misc import derive_section_root


class BaseAPIViewArgumentForm(forms.Form):
    """
    A form class that accepts 'view' and 'request' arguments at initialisation,
    is capable of rendering itself to a template (in a similar fashion to
    ``django_filters.rest_framework.DjangoFilterBackend``), and has some
    custom cleaning behaviour to better handle missing values.
    """

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

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
        if 'crispy_forms' in settings.INSTALLED_APPS:
            return 'wagtailmenus/api/forms/crispy_form.html'
        return 'wagtailmenus/api/forms/form.html'

    def to_html(self, request):
        template = loader.get_template(self.template_name)
        context = {'form': self}
        return template.render(context, request)

    @property
    def helper(self):
        if 'crispy_forms' not in settings.INSTALLED_APPS:
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
    current_url = forms.URLField(
        label='current_url',
        max_length=300,
        required=False,
        help_text=_(
            "The full URL of the page you are generating the menu for, "
            "including scheme and domain. For example: "
            "'https://www.example.com/about-us/')."
        ),
    )
    current_page_id = api_form_fields.PageChoiceField(
        label='current_page_id',
        required=False,
        help_text=_(
            "The ID of the Wagtail Page you are generating the menu for, "
            "if applicable."
        ),
    )
    max_levels = api_form_fields.MaxLevelsChoiceField(
        label='max_levels',
        required=False,
        help_text=_(
            "The maximum number of levels of menu items that should be "
            "included in the result. Defaults to the relevant setting value "
            "for this menu type."
        )
    )
    apply_active_classes = api_form_fields.BooleanChoiceField(
        label='apply_active_classes',
        required=False,
        initial=False,
        help_text=_(
            "Whether the view should set 'active_class' attributes on menu "
            "items to help indicate a user's current position within the menu "
            "structure. Defaults to 'false'. If providing a value of 'true', "
            "'current_page_id' or 'current_url' must also be provided."
        ),
    )
    allow_repeating_parents = api_form_fields.BooleanChoiceField(
        label='allow_repeating_parents',
        required=False,
        initial=False,
        help_text=_(
            "Whether the view should allow pages inheriting from MenuPage or "
            "MenuPageMixin to add duplicates of themselves to their "
            "'children' when appearing as menu items. Defaults to the "
            "relevant setting value for this menu type."
        )
    )
    relative_page_urls = api_form_fields.BooleanChoiceField(
        label='relative_page_urls',
        required=False,
        initial=False,
        help_text=_(
            "Whether the view should use relative URLs for page links instead "
            "of absolute ones. Defaults to 'false'. If providing a value of "
            "'true', 'current_page_id' or 'current_url' must also be provided."
        )
    )
    language = forms.ChoiceField(
        label='language',
        required=False,
        choices=settings.LANGUAGES,
        initial=settings.LANGUAGE_CODE,
        help_text=_(
            "The language you wish to rendering the menu in. Must be one of "
            "the languages defined in your LANGUAGES setting. Will only "
            "affect the result if USE_I18N is True. Defaults to LANGUAGE_CODE."
        )
    )

    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['current_page_id'].queryset = Page.objects.filter(depth__gt=1)
        if not settings.USE_I18N:
            self.fields['language'].widget = forms.HiddenInput()

    def clean_current_page_id(self):
        value = self.cleaned_data['current_page_id']
        # Set 'current_page' to the page object (or None)
        self.cleaned_data['current_page'] = value
        if value:
            # Use the page PK for 'current_page_id'
            return value.pk
        return value

    def clean(self):
        data = super().clean()
        for field_name in ('apply_active_classes', 'relative_page_urls'):
            if data.get(field_name):
                if not data.get("current_page_id") and not data.get("current_url"):
                    self.add_error(field_name, (
                        "To support a value of 'true', 'current_page_id' or "
                        "'current_url' values must also be provided."
                    ))
                elif not data.get('current_page') and not data.get('best_match_page'):
                    self.derive_current_or_best_match_page()

    def derive_current_site(self):
        """
        Attempts to derive a 'current_site' value from other values in
        ``cleaned_data`` and update ``cleaned_data`` with the value.
        """
        data = self.cleaned_data

        site_page = data.get('current_page') or \
            data.get('parent_page') or \
            data.get('section_root_page')

        func = api_settings.objects.CURRENT_SITE_DERIVATION_FUNCTION
        data['current_site'] = func(
            self.request, site_page, data['current_url']
        )

    def derive_current_or_best_match_page(self):
        """
        Attempts to identify a ``Page`` from the 'current_url` value in
        ``cleaned_data``. If a page is found matching the full URL, it will
        be added to ``cleaned_data`` as 'current_page'. Otherwise, it will
        be added as 'best_match_page'.
        """
        data = self.cleaned_data

        if not data.get('current_site'):
            self.derive_current_site()

        func = api_settings.objects.CURRENT_PAGE_DERIVATION_FUNCTION
        result, full_url_match = func(
            self.request,
            data['current_site'],
            data.get('current_url'),
        )

        if not result:
            return
        elif full_url_match:
            data['current_page'] = result
        else:
            data['best_match_page'] = result


class BaseMenuModelGeneratorArgumentForm(BaseMenuGeneratorArgumentForm):
    max_levels = api_form_fields.MaxLevelsChoiceField(
        label='max_levels',
        required=False,
        empty_label=_('Default: Use the value set for the menu object'),
        help_text=_(
            "The maximum number of levels of menu items that should be "
            "included in the result. Defaults to the 'max_levels' field value "
            "on the matching menu object."
        ),
    )

    def clean(self):
        data = self.cleaned_data

        if not data.get("current_page_id") and not data.get("current_url"):
            self.add_error('current_page_id', (
                "This or 'current_url' are required to allow the "
                "correct menu instance to be identified."
            ))
            return

        if not data.get('current_site'):
            self.derive_current_site()

        return super().clean()


class MainMenuGeneratorArgumentForm(BaseMenuModelGeneratorArgumentForm):
    field_order = (
        'current_page_id',
        'current_url',
        'max_levels',
        'apply_active_classes',
        'allow_repeating_parents',
        'relative_page_urls',
        'language',
    )


class FlatMenuGeneratorArgumentForm(BaseMenuModelGeneratorArgumentForm):
    handle = api_form_fields.FlatMenuHandleField(
        label='handle',
        help_text=_(
            "The 'handle' for the flat menu you wish to generate. For "
            "example: 'info' or 'contact'."
        )
    )
    fall_back_to_default_site_menus = api_form_fields.BooleanChoiceField(
        label=_('fall_back_to_default_site_menus'),
        required=False,
        help_text=_(
            "If a menu cannot be found matching the provided 'handle' for the "
            "site indicated by 'current_url' or 'current_page_id', use the "
            "flat menu defined for the 'default' site (if available). "
            "Defaults to 'false'."
        )
    )

    field_order = (
        'handle',
        'current_page_id',
        'current_url',
        'fall_back_to_default_site_menus',
        'max_levels',
        'apply_active_classes',
        'allow_repeating_parents',
        'relative_page_urls',
        'language',
    )


class ChildrenMenuGeneratorArgumentForm(BaseMenuGeneratorArgumentForm):

    parent_page_id = api_form_fields.PageChoiceField(
        label='parent_page_id',
        help_text=_(
            "The ID of the page you want the menu to show children page links "
            "for."
        )
    )

    field_order = (
        'parent_page_id',
        'current_page_id',
        'current_url',
        'max_levels',
        'apply_active_classes',
        'allow_repeating_parents',
        'relative_page_urls',
        'language',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent_page_id'].queryset = Page.objects.filter(depth__gt=1)

    def clean_parent_page_id(self):
        value = self.cleaned_data['parent_page_id']
        # Set 'parent_page' to the page object (or None)
        self.cleaned_data['parent_page'] = value
        if value:
            # Use the page PK for 'parent_page_id'
            return value.pk
        return value


class SectionMenuGeneratorArgumentForm(BaseMenuGeneratorArgumentForm):

    section_root_page_id = api_form_fields.PageChoiceField(
        label='section_root_page_id',
        required=False,
        indent_choice_labels=False,
        help_text=_(
            "The ID of the 'section root page' you want the menu to show "
            "descendant page links for. If not supplied, the endpoint will "
            "attempt to derive this from 'current_url' or 'current_page_id'."
        )
    )

    field_order = (
        'section_root_page_id',
        'current_page_id',
        'current_url',
        'max_levels',
        'apply_active_classes',
        'allow_repeating_parents',
        'relative_page_urls',
        'language',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['section_root_page_id'].queryset = Page.objects.filter(
            depth__exact=wagtailmenus_settings.SECTION_ROOT_DEPTH)

    def clean_section_root_page_id(self):
        value = self.cleaned_data['section_root_page_id']
        # Set 'section_root_page' to the page object (or None)
        self.cleaned_data['section_root_page'] = value
        if value:
            # Use the page PK for 'section_root_page_id'
            return value.pk
        return value

    def clean(self):
        if not self.cleaned_data.get('section_root_page'):
            self.derive_section_root_page()
        return super().clean()

    def derive_section_root_page(self):
        data = self.cleaned_data

        if not data.get("current_page_id") and not data.get("current_url"):
            self.add_error('section_root_page', (
                "This value can only be ommitted when providing 'current_page' "
                "or 'current_url'."
            ))
            return

        if not data.get('current_page'):
            self.derive_current_or_best_match_page()

        section_root = derive_section_root(
            data.get('current_page') or data.get('best_match_page')
        )
        if section_root:
            data['section_root_page'] = section_root
            data['section_root_page_id'] = section_root.pk

        else:
            self.add_error('section_root_page', (
                "This value could not be derived from the 'current_page' or "
                "'current_url' values provided."
            ))
