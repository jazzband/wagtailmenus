from django.template import RequestContext
from django.test.client import RequestFactory
from wagtailmenus.conf import constants
from wagtailmenus.models.menus import ContextualVals, OptionVals


SUB_MENU_TEMPLATE_LIST = (
    'menus/sub_menu_level_2.html',
    'menus/sub_menu_level_3.html',
)
SINGLE_ITEM_SUB_MENU_TEMPLATE_LIST = ('menus/sub_menu_level_2.html',)


def get_page_model():
    try:
        from wagtail.models import Page
    except ImportError:
        from wagtail.core.models import Page
    return Page


def get_site_model():
    try:
        from wagtail.models import Site
    except ImportError:
        from wagtail.core.models import Site
    return Site


def make_optionvals_instance(
    max_levels=2,
    apply_active_classes=True,
    allow_repeating_parents=True,
    use_absolute_page_urls=False,
    add_sub_menus_inline=False,
    parent_page=None,
    handle=None,
    template_name=None,
    sub_menu_template_name=None,
    sub_menu_template_names=None,
    extra={},
):
    return OptionVals(
        max_levels,
        apply_active_classes,
        allow_repeating_parents,
        use_absolute_page_urls,
        add_sub_menus_inline,
        parent_page,
        handle,
        template_name,
        sub_menu_template_name,
        sub_menu_template_names,
        extra
    )


def make_contextualvals_instance(
    url='/',
    request=None,
    parent_context=None,
    current_site=None,
    current_level=1,
    original_menu_tag='',
    original_menu_instance=None,
    current_page=None,
    current_section_root_page=None,
    current_page_ancestor_ids=(),
):
    if request is None:
        rf = RequestFactory()
        request = rf.get(url)
    if parent_context is None:
        parent_context = RequestContext(request, {})
    return ContextualVals(
        parent_context,
        request,
        current_site,
        current_level,
        original_menu_tag,
        original_menu_instance,
        current_page,
        current_section_root_page,
        current_page_ancestor_ids,
    )
