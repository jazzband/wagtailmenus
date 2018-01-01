from django.http import Http404
from django.utils.functional import SimpleLazyObject
from . import app_settings
from .utils.misc import get_site_from_request


def wagtailmenus(request):

    def _get_value_dict():
        current_page = request.META.get('WAGTAILMENUS_CURRENT_PAGE')
        section_root = request.META.get('WAGTAILMENUS_CURRENT_SECTION_ROOT')
        ancestor_ids = request.META.get(
            'WAGTAILMENUS_CURRENT_PAGE_ANCESTOR_IDS')
        match = None
        site = get_site_from_request(request, fallback_to_default=True)

        guess_pos = app_settings.GUESS_TREE_POSITION_FROM_PATH
        sroot_depth = app_settings.SECTION_ROOT_DEPTH

        if guess_pos and not current_page:
            path_components = [pc for pc in request.path.split('/') if pc]
            # Keep trying to find a page using the path components until there
            # are no components left, or a page has been identified
            first_run = True
            while path_components and match is None:
                try:
                    match, args, kwargs = site.root_page.specific.route(
                        request, path_components)
                    ancestor_ids = match.get_ancestors(inclusive=True).filter(
                        depth__gte=sroot_depth).values_list('id', flat=True)
                    if first_run:
                        # A page was found matching the exact path, so it's
                        # safe to assume it's the 'current page'
                        current_page = match
                except Http404:
                    # No match found, so remove a path component and try again
                    path_components.pop()
                first_run = False

        if guess_pos and not section_root:
            best_match = current_page or match
            if best_match:
                if best_match.depth == sroot_depth:
                    section_root = best_match
                elif best_match.depth > sroot_depth:
                    # Attempt to identify the section root page from best_match
                    section_root = best_match.get_ancestors().filter(
                        depth__exact=sroot_depth).first()

        return {
            'current_page': current_page,
            'section_root': section_root,
            'current_page_ancestor_ids': ancestor_ids or (),
        }

    return {
        'wagtailmenus_vals': SimpleLazyObject(_get_value_dict),
        'USE_SPECIFIC_OFF': app_settings.USE_SPECIFIC_OFF,
        'USE_SPECIFIC_AUTO': app_settings.USE_SPECIFIC_AUTO,
        'USE_SPECIFIC_TOP_LEVEL': app_settings.USE_SPECIFIC_TOP_LEVEL,
        'USE_SPECIFIC_ALWAYS': app_settings.USE_SPECIFIC_ALWAYS,
    }
