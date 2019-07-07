from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from wagtail.core.models import Page, Site

from wagtailmenus.conf import constants, settings


class JavascriptStyleBooleanSelect(forms.Select):

    def __init__(self, attrs=None):
        choices = (
            ('true', _('Yes')),
            ('false', _('No')),
        )
        super().__init__(attrs, choices)

    def format_value(self, value):
        try:
            return {
                True: 'true',
                False: 'false',
                'True': 'true',
                'False': 'false',
                'true': 'true',
                'false': 'false',
                1: 'true',
                0: 'false',
                '1': 'true',
                '0': 'false',
            }[value]
        except KeyError:
            return ''

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        return {
            True: True,
            False: False,
            'True': True,
            'False': False,
            'true': True,
            'false': False,
            '1': True,
            '0': False,
        }.get(value)


class BooleanChoiceField(forms.BooleanField):
    widget = JavascriptStyleBooleanSelect

    def clean(self, value):
        if value is None:
            raise ValidationError("The value must be 'true' or 'false'.", code="invalid")
        return value


class UseSpecificChoiceField(forms.TypedChoiceField):

    default_error_messages = {
        'invalid_choice': _('The provided value is not supported.')
    }

    def __init__(self, *args, **kwargs):
        empty_label = kwargs.pop('empty_label', '-----')
        choices = (('', empty_label),) + constants.USE_SPECIFIC_CHOICES
        defaults = {
            'choices': choices,
            'coerce': int,
            'empty_value': None,
        }
        kwargs.update({k: v for k, v in defaults.items() if k not in kwargs})
        super().__init__(*args, **kwargs)


class MaxLevelsChoiceField(forms.TypedChoiceField):

    default_error_messages = {
        'invalid_choice': _('The provided value is not a supported.')
    }

    def __init__(self, *args, **kwargs):
        empty_label = kwargs.pop('empty_label', '-----')
        choices = (('', empty_label),) + constants.MAX_LEVELS_CHOICES
        defaults = {
            'choices': choices,
            'coerce': int,
            'empty_value': None,
        }
        kwargs.update({k: v for k, v in defaults.items() if k not in kwargs})
        super().__init__(*args, **kwargs)


class PageChoiceField(forms.ModelChoiceField):

    default_error_messages = {
        'invalid_choice': _('The provided value is not a valid page ID.')
    }

    def __init__(self, *args, **kwargs):
        if 'queryset' not in 'kwargs':
            kwargs['queryset'] = Page.objects.none()
        super().__init__(*args, **kwargs)


class SiteChoiceField(forms.ModelChoiceField):

    default_error_messages = {
        'invalid_choice': _('The provided valie is not a valid site ID.')
    }

    def __init__(self, *args, **kwargs):
        if 'queryset' not in 'kwargs':
            kwargs['queryset'] = Site.objects.none()
        super().__init__(*args, **kwargs)


class FlatMenuHandleField(forms.SlugField):

    def __init__(self, *args, **kwargs):
        if settings.FLAT_MENUS_HANDLE_CHOICES:
            kwargs['widget'] = forms.Select(choices=settings.FLAT_MENUS_HANDLE_CHOICES)
        super().__init__(*args, **kwargs)
