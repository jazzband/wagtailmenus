from io import StringIO
from urllib.parse import urlparse

from django.conf import settings
from django.core.handlers.base import BaseHandler
from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404, HttpRequest
from wagtail.core.models import Page, Site

from wagtailmenus.models.menuitems import MenuItem


def get_fake_site():
    site = Site()
    site.id = 0
    site.pk = 0
    return site


def get_fake_request():
    """
    Return a HttpRequest that can be passed to page url
    methods to benefit from caching of site root paths.
    """
    request = HttpRequest()
    request.method = "GET"
    request.path = "/"
    request.META["SERVER_NAME"] = "localhost"
    site = get_fake_site()
    request.site = site  # for Wagtail < 2.9
    request._wagtail_site = site  # For Wagtail >= 2.9
    return request


def get_site_from_request(request, fallback_to_default=True):
    site = getattr(request, 'site', None)
    if isinstance(site, Site):
        return request.site
    site = Site.find_for_request(request)
    if site:
        return site
    if fallback_to_default:
        return Site.objects.filter(is_default_site=True).first()
    return None


def derive_page(request, site, accept_best_match=True, max_subsequent_route_failures=3):
    """
    Attempts to find a ``Page`` from the provided ``site`` matching the path
    of the supplied ``request``. Returns a tuple, where the first item is
    the matching page (or ``None`` if no match was found), and the second item
    is a boolean indicating whether the page matched the full URL.

    If ``accept_best_match`` is ``True``, the method will attempt to find a
    'best match', matching as many path components as possible. This process
    will continue until all path components have been exhausted, or routing
    fails more that ``max_subsequent_route_failures`` times in a row.
    """
    routing_point = site.root_page.specific
    path_components = [pc for pc in request.path.split('/') if pc]

    if not accept_best_match:
        try:
            return routing_point.route(request, path_components)[0], True
        except Http404:
            return None, False

    best_match = None
    full_url_match = False
    lookup_components = []
    subsequent_route_failures = 0

    for i, component in enumerate(path_components, 1):
        lookup_components.append(component)
        try:
            best_match = routing_point.route(request, lookup_components)[0]
        except Http404:
            # route() was unsucessful. keep trying with more components until
            # they are exhausted, or the maximum number of subsequent failures
            # has been reached
            subsequent_route_failures += 1
            if subsequent_route_failures >= max_subsequent_route_failures:
                break  # give up
        else:
            # route() was successful. have all components been used yet?
            full_url_match = bool(i == len(path_components))

            # reset failure count
            subsequent_route_failures = 0

            if best_match != routing_point:
                # A new page was reached. Next, try route() from this new
                # page, using fresh lookup components
                routing_point = best_match
                lookup_components = []
            else:
                # `routing_point` has multiple routes. Next, try route() from
                # the same page with more components, as a new page could still
                # be reached
                continue

    return best_match, full_url_match


def derive_section_root(page):
    """
    Returns the 'section root' for the provided ``page``, or ``None``
    if no such page can be identified. Results are dependant on the
    value of the ``WAGTAILMENUS_SECTION_ROOT_DEPTH`` setting.
    """
    from wagtailmenus.conf import settings

    desired_depth = settings.SECTION_ROOT_DEPTH
    if page.depth == desired_depth:
        return page.specific
    if page.depth > desired_depth:
        return page.get_ancestors().get(depth=desired_depth).specific


def make_dummy_request(url, original_request, **metadata):
    """
    Construct a HttpRequest object that is, as far as possible,
    representative of the original request - only for the provided ``url``
    instead of the one that was originally requested.
    """
    url_info = urlparse(url)
    hostname = url_info.hostname
    path = url_info.path
    port = url_info.port or 80
    scheme = url_info.scheme

    dummy_values = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': path,
        'SERVER_NAME': hostname,
        'SERVER_PORT': port,
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'HTTP_HOST': hostname,
        'wsgi.version': (1, 0),
        'wsgi.input': StringIO(),
        'wsgi.errors': StringIO(),
        'wsgi.url_scheme': scheme,
        'wsgi.multithread': True,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }

    # Add important values from the original request object
    headers_to_copy = [
        'REMOTE_ADDR', 'HTTP_X_FORWARDED_FOR', 'HTTP_COOKIE',
        'HTTP_USER_AGENT', 'HTTP_AUTHORIZATION', 'wsgi.version',
        'wsgi.multithread', 'wsgi.multiprocess', 'wsgi.run_once',
    ]
    if settings.SECURE_PROXY_SSL_HEADER:
        headers_to_copy.append(settings.SECURE_PROXY_SSL_HEADER[0])
    for header in headers_to_copy:
        if header in original_request.META:
            dummy_values[header] = original_request.META[header]

    # Add additional custom metadata sent by the caller.
    dummy_values.update(**metadata)

    request = WSGIRequest(dummy_values)

    # Add a flag to let middleware know that this is a dummy request.
    request.is_dummy = True

    # Apply middleware to the request
    handler = BaseHandler()
    handler.load_middleware()
    handler._middleware_chain(request)

    return request


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
