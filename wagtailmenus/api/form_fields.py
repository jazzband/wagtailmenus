from functools import lru_cache

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from wagtail.core.models import Page, Site

from wagtailmenus.conf import constants, settings


@lru_cache(maxsize=64)
def get_label_indent(depth, indent_string):
    if depth > 1:
        return ''.join(str(indent_string) for i in range(depth-2))
    return ''


class IndentedPageChoiceIterator(forms.models.ModelChoiceIterator):
    indent_string = '    - '

    def __init__(self, field):
        self.field = field
        # Limit fields to help with performance
        self.queryset = field.queryset.only('id', 'depth', 'title')

    def label_from_instance(self, obj):
        # Indent field labels according to depth (if enabled)
        if self.field.indent_choice_labels:
            return '{indent}{title}'.format(
                indent=get_label_indent(obj.depth, self.indent_string),
                title=obj.title,
            )
        return obj.title

    def choice(self, obj):
        # Use the above label_from_instance() method instead
        # of the one
        return (self.field.prepare_value(obj), self.label_from_instance(obj))


class JavascriptStyleBooleanSelect(forms.Select):

    def __init__(self, attrs=None):
        choices = (
            ('true', _('true')),
            ('false', _('false')),
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


class PageIDChoiceField(forms.ModelChoiceField):

    default_error_messages = {
        'invalid_choice': _('The provided value is not a valid page ID.')
    }

    iterator = IndentedPageChoiceIterator

    def __init__(self, *args, **kwargs):
        if 'queryset' not in kwargs:
            kwargs['queryset'] = Page.objects.filter(depth__gt=1)
        self.indent_choice_labels = kwargs.pop('indent_choice_labels', True)
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
