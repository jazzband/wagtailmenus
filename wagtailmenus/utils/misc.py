from django.http import Http404
from wagtail.core.models import Page, Site

from wagtailmenus.models.menuitems import MenuItem


def get_site_from_request(request, fallback_to_default=True):
    if getattr(request, 'site', None):
        return request.site
    if fallback_to_default:
        return Site.objects.filter(is_default_site=True).first()
    return None


def get_page_from_request(request, site, accept_best_match=True):
    """
    Attempts to find a ``Page`` within ``site`` for the supplied
    ``request``. Returns a tuple, where the first element is the matching
    ``Page`` object (or ``None`` if no match was found), and a boolean
    indicating whether the page matched the full URL.

    If ``accept_best_match`` is ``True``, and a page cannot be found
    matching the full URL, the method will attempt to find a 'best match'
    for the request instead.
    """
    routing_point = site.root_page.specific
    path_components = [pc for pc in request.path.split('/') if pc]

    if not accept_best_match:
        # Attempt to find a full URL match, or give up
        try:
            return routing_point.route(request, path_components)[0], True
        except Http404:
            return None, False

    best_match = None
    full_url_match = False
    lookup_components = []

    # Keep trying to route() until path components are exhausted
    for i, component in enumerate(path_components, 1):
        lookup_components.append(component)
        try:
            best_match = routing_point.route(request, lookup_components)[0]
            full_url_match = bool(i == len(path_components))
            if best_match != routing_point:
                # A new page was reached. Next time, try routing from this new
                # page, using a single lookup component
                routing_point = best_match
                lookup_components = []
            else:
                # It looks like `routing_point` has multiple routes. Next time,
                # try routing from the same page with more components
                continue
        except Http404:
            # No luck this time, but keep trying with more components until
            # a new page is reached, or there are no components left.
            continue

    return best_match, full_url_match


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
