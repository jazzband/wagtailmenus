from wagtail.core.models import Page, Site

from wagtailmenus.models.menuitems import MenuItem


def get_site_from_request(request, fallback_to_default=True):
    if getattr(request, 'site', None):
        return request.site
    if fallback_to_default:
        return Site.objects.filter(is_default_site=True).first()
    return None


def validate_supplied_values(tag, max_levels=None, parent_page=None,
                             menuitem_or_page=None):
    if max_levels is not None:
        if max_levels not in (1, 2, 3, 4, 5):
            raise ValueError(
                "The `%s` tag expects `max_levels` to be an integer value "
                "between 1 and 5. Please review your template." % tag
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
