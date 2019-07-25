from django.http import Http404
from django.utils.functional import SimpleLazyObject

from wagtailmenus.conf import constants, settings
from wagtailmenus.utils.misc import (
    derive_page, derive_section_root, derive_ancestor_ids,
    get_site_from_request
)


def wagtailmenus(request):

    def _get_wagtailmenus_vals():
        current_page = request.META.get('WAGTAILMENUS_CURRENT_PAGE')
        section_root = request.META.get('WAGTAILMENUS_CURRENT_SECTION_ROOT')
        site = get_site_from_request(request)
        ancestor_ids = ()
        guess_position = settings.GUESS_TREE_POSITION_FROM_PATH
        best_match_page = None

        if guess_position and not current_page:
            best_match_page, full_url_match = derive_page(request, site)
            if full_url_match:
                current_page = best_match_page

        if not section_root:
            section_root = derive_section_root(current_page or best_match_page)

        ancestor_ids = derive_ancestor_ids(current_page or best_match_page)

        return {
            'current_page': current_page,
            'section_root': section_root,
            'current_page_ancestor_ids': ancestor_ids,
        }

    return {
        'wagtailmenus_vals': SimpleLazyObject(_get_wagtailmenus_vals),
    }
