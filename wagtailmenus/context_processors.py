from __future__ import unicode_literals

from django.http import Http404
from django.utils.functional import SimpleLazyObject

from .app_settings import SECTION_ROOT_DEPTH, GUESS_TREE_POSITION_FROM_PATH


def wagtailmenus(request):

    def _get_value_dict():
        current_page = request.META.get('WAGTAILMENUS_CURRENT_PAGE')
        section_root = request.META.get('WAGTAILMENUS_CURRENT_SECTION_ROOT')
        ancestor_ids = request.META.get(
            'WAGTAILMENUS_CURRENT_PAGE_ANCESTOR_IDS')
        match = None
        site = request.site

        if GUESS_TREE_POSITION_FROM_PATH and not current_page:
            path_components = [pc for pc in request.path.split('/') if pc]
            # Keep trying to find a page using the path components until there
            # are no components left, or a page has been identified
            first_run = True
            while path_components and match is None:
                try:
                    match, args, kwargs = site.root_page.specific.route(
                        request, path_components)
                    ancestor_ids = match.get_ancestors(inclusive=True).filter(
                        depth__gte=SECTION_ROOT_DEPTH
                    ).values_list('id', flat=True)
                    if first_run:
                        # A page was found matching the exact path, so it's
                        # safe to assume it's the 'current page'
                        current_page = match
                except Http404:
                    # No match found, so remove a path component and try again
                    path_components.pop()
                first_run = False

        best_match = current_page or match
        if GUESS_TREE_POSITION_FROM_PATH and not section_root and best_match:
            if best_match.depth == SECTION_ROOT_DEPTH:
                section_root = best_match
            elif best_match.depth > SECTION_ROOT_DEPTH:
                # Attempt to identify the section root page from best_match
                section_root = best_match.get_ancestors().filter(
                    depth__exact=SECTION_ROOT_DEPTH).first()

        return {
            'current_page': current_page,
            'section_root': section_root,
            'current_page_ancestor_ids': ancestor_ids or (),
        }

    return {
        'wagtailmenus_vals': SimpleLazyObject(_get_value_dict)
    }
