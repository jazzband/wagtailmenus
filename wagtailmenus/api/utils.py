from io import StringIO
from urllib.parse import urlparse

from django.conf import settings
from django.core.handlers.base import BaseHandler
from django.core.handlers.wsgi import WSGIRequest
from wagtail.core.sites import get_site_for_hostname

from wagtailmenus.utils.misc import derive_page


def derive_current_site(request, site_page, url):
    """
    Attempts to find a ``Site`` object for the current ``request``.
    using the supplied ``site_page`` or ``url``.

    This function makes some assumptions about how Wagtail is being
    used, and might not be appropriate for all implementations.
    If needed, you can implement an alternative derivation function
    (accepting the same arguments as this one) and register it using the
    ``WAGTAILMENUS_API_V1_CURRENT_SITE_DERIVATION_FUNCTION`` setting.
    """
    if site_page is not None:
        return site_page.get_site()
    parsed_url = urlparse(url)
    port = parsed_url.port or 443 if parsed_url.scheme == 'https' else 80
    return get_site_for_hostname(parsed_url.hostname, port)


def derive_current_page(request, site, url):
    """
    Attempts to find a ``Page`` object matching the supplied ``url`` for the
    current API ``request``. Returns a tuple with two items, where the first
    is the matching ``Page`` (or ``None`` if no match was found), and the
    second a boolean indicating whether the match was an exact match for
    the URL (or ``False`` if no match was found).

    This function uses Wagtail's built-in page routing mechanism to find
    a matching page. In order to do this, a 'dummy request' is created from
    ``api_request`` for the supplied ``url``. This approach might not be
    appropriate for all implementations. If needed, you can implement an
    alternative derivation function (accepting the same arguments as this one)
    and register it using the ``WAGTAILMENUS_API_V1_CURRENT_PAGE_DERIVATION_FUNCTION``
    setting.
    """

    # Create a dummy request is created for the supplied URL, but otherwise
    # matching
    dummy_request = make_dummy_request(url, request)
    return derive_page(dummy_request, site)


def make_dummy_request(url, original_request, **metadata):
    """
    Construct a HttpRequest object that is, as far as possible,
    representative of the original request - only for the provided ``url``
    instead of the one that was originally requested.
    """
    url_info = urlparse(url)
    hostname = url_info.hostname
    path = url_info.path
    port = url_info.port or (443 if url_info.scheme == 'https' else 80)
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


def make_serializer_class(name, base_class, field_names, model=None, field_serializer_overrides=None, **additional_attributes):
    _model = model

    if _model is not None:
        class Meta:
            model = _model
            fields = list(field_names)
    else:
        class Meta:
            fields = list(field_names)

    attrs = {'Meta': Meta}

    if field_serializer_overrides:
        attrs.update(field_serializer_overrides)

    attrs.update(additional_attributes)

    return type(name, (base_class, ), attrs)
