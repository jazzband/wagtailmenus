from django.utils import translation


class TranslatedField(object):
    def __init__(self, en_field, de_field, fr_field):
        self.en_field = en_field
        self.de_field = de_field
        self.fr_field = fr_field

    def __get__(self, instance, owner):
        english = getattr(instance, self.en_field)
        trans_field_name = '%s_field' % translation.get_language()
        trans_field = getattr(self, trans_field_name, None)
        if trans_field:
            return getattr(instance, trans_field) or english
        return english
