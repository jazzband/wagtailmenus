from rest_framework.serializers import ModelSerializer

from wagtail.api.v2.serializers import PageTypeField


class BasePageSerializer(ModelSerializer):
    """
    Used to render 'page' info for menu items. This could be a ``link_page``
    value for a model-based menu item (e.g. a ``MainMenuItem`` or
    ``FlatMenuItem`` object), or a representation of the menu item itself (if
    the menu item is in fact a ``Page`` object).
    """
    type = PageTypeField(read_only=True)
