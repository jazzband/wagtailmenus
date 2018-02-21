from wagtail import VERSION as WAGTAIL_VERSION
if WAGTAIL_VERSION >= (2, 0):
    from wagtail.core.models import Page, Site
else:
    from wagtail.wagtailcore.models import Page, Site

from ..models.menuitems import MenuItem


def get_site_from_request(request, fallback_to_default=True):
    if getattr(request, 'site', None):
        return request.site
    if fallback_to_default:
        return Site.objects.filter(is_default_site=True).first()
    return None


def validate_supplied_values(tag, max_levels=None, use_specific=None,
                             parent_page=None, menuitem_or_page=None):
    if max_levels is not None:
        if max_levels not in (1, 2, 3, 4, 5):
            raise ValueError(
                "The `%s` tag expects `max_levels` to be an integer value "
                "between 1 and 5. Please review your template." % tag
            )
    if use_specific is not None:
        if use_specific not in (0, 1, 2, 3):
            raise ValueError(
                "The `%s` tag expects `use_specific` to be an integer value "
                "between 0 and 3. Please review your template." % tag
            )
    if parent_page is not None:
        if not isinstance(parent_page, Page):
            raise ValueError(
                "The `%s` tag expects `parent_page` to be a `Page` instance. "
                "A value of type `%s` was supplied." %
                (tag, parent_page.__class__)
            )
    if menuitem_or_page is not None:
        if not isinstance(menuitem_or_page, (Page, MenuItem)):
            raise ValueError(
                "The `%s` tag expects `menuitem_or_page` to be a `Page` or "
                "`MenuItem` instance. A value of type `%s` was supplied." %
                (tag, menuitem_or_page.__class__)
            )
