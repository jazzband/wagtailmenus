from django.conf import settings

from wagtail.core.models import Page
from wagtailmenus.conf import settings as wagtailmenus_settings
from wagtailmenus.api.utils import make_serializer_class

from rest_framework import serializers



class BaseMenuOptionSerializer(serializers.Serializer):
    current_page_id = api_form_fields.PageIDChoiceField(
        label='current_page_id',
        required=False,
        help_text=_(
            "The ID of the Wagtail Page you are generating the menu for "
            "(if available)."
        ),
    )
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
    max_levels = api_form_fields.MaxLevelsChoiceField(
        label='max_levels',
        required=False,
        help_text=_(
            "The maximum number of levels of menu items that should be "
            "included in the result. Defaults to the relevant setting value "
            "for this menu type."
        )
    )
    current_site_id = api_form_fields.SiteIDChoiceField(
        label='current_site_id',
        required=False,
        help_text=_(
            "The ID of the Wagtail 'Site' you are generating the menu for "
            "(if available)."
        ),
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

    max_levels_default = None
    allow_repeating_parents_default = True

    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['current_page_id'].queryset = Page.objects.filter(depth__gt=1)
        if not settings.USE_I18N:
            self.fields.pop('language')
        if api_settings.SINGLE_SITE_MODE:
            self.fields.pop('current_site_id')

    def get_default_option_values(self):
        return {
            'max_levels': self.max_levels_default,
            'allow_repeating_parents': self.allow_repeating_parents_default,
        }

    def clean_current_site_id(self):
        value = self.cleaned_data['current_site_id']
        # Set 'current_site' to the page object (or None)
        self.cleaned_data['current_site'] = value
        if value:
            # Use the page PK for 'current_site_id'
            return value.pk
        return value

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

        if data.get('relative_page_urls'):
            if(
                not api_settings.SINGLE_SITE_MODE and
                not data.get("current_site_id") and
                not data.get("current_page_id") and
                not data.get("current_url")
            ):
                self.add_error('relative_page_urls', (
                    "To use relative page URLs, one of the following must "
                    "also be provided: 'current_site_id', 'current_page_id' "
                    "or 'current_url'. For single-site projects, you might "
                    "also consider enabling SINGLE_SITE_MODE."
                ))
            elif not data.get('current_site'):
                self.derive_current_site()

        if data.get('apply_active_classes'):
            if not data.get("current_page_id") and not data.get("current_url"):
                self.add_error('apply_active_classes', (
                    "To apply active classes, one of the following must also "
                    "be provided: 'current_page_id' or 'current_url'."
                ))
            elif not data.get('current_page') and not data.get('best_match_page'):
                self.derive_current_or_best_match_page()

    def derive_current_site(self):
        """
        Attempts to derive a 'current_site' value from other values in
        ``cleaned_data`` and update ``cleaned_data`` with the value.
        """
        data = self.cleaned_data

        if api_settings.SINGLE_SITE_MODE:
            data['current_site'] = Site.objects.all().first()
            return

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


class BaseModelMenuOptionSerializer(BaseMenuOptionSerializer):
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

        if not data.get('current_site'):

            if(
                not api_settings.SINGLE_SITE_MODE and
                not data.get("current_page_id") and
                not data.get("current_url")
            ):
                self.add_error('current_site', (
                    "You must provide this, 'current_page_id' or 'current_url' "
                    "to allow the relevant menu to be identified."
                ))
            else:
                self.derive_current_site()

        return super().clean()


class MainMenuOptionSerializer(BaseModelMenuOptionSerializer):
    field_order = (
        'current_site_id',
        'current_page_id',
        'current_url',
        'max_levels',
        'apply_active_classes',
        'allow_repeating_parents',
        'relative_page_urls',
        'language',
    )


class FlatMenuOptionSerializer(BaseModelMenuOptionSerializer):
    handle = api_form_fields.FlatMenuHandleField(
        label='handle',
        help_text=_(
            "The 'handle' for the flat menu you wish to generate. For "
            "example: 'info' or 'contact'."
        )
    )
    fall_back_to_default_site_menus = api_form_fields.BooleanChoiceField(
        label=_('fall_back_to_default_site_menus'),
        default=True,
        required=False,
        help_text=_(
            "If a menu cannot be found matching the provided 'handle' for the "
            "site indicated by 'current_url' or 'current_page_id', use the "
            "flat menu defined for the 'default' site (if available). "
            "Defaults to 'false'."
        )
    )

    field_order = (
        'current_site_id',
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


class ChildrenMenuOptionSerializer(BaseMenuOptionSerializer):
    parent_page_id = api_form_fields.PageIDChoiceField(
        label='parent_page_id',
        help_text=_(
            "The ID of the page you want the menu to show children page links "
            "for."
        )
    )

    field_order = (
        'parent_page_id',
        'current_site_id',
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


class SectionMenuOptionSerializer(BaseMenuOptionSerializer):
    section_root_page_id = api_form_fields.PageIDChoiceField(
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
        'current_site_id',
        'current_page_id',
        'current_url',
        'max_levels',
        'apply_active_classes',
        'allow_repeating_parents',
        'relative_page_urls',
        'language',
    )

    # argument defaults
    max_levels_default = wagtailmenus_settings.DEFAULT_SECTION_MENU_MAX_LEVELS

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

        if not data.get('current_page_id') and not data.get('current_url'):
            self.add_error('section_root_page_id', (
                "This value can only be ommitted when providing "
                "'current_page_id' or 'current_url'."
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
            self.add_error('section_root_page_id', (
                "This value could not be derived from the 'current_page_id' "
                "or 'current_url' values provided."
            ))
