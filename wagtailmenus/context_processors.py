from django.utils.functional import SimpleLazyObject

from wagtailmenus.conf import settings
from wagtailmenus.utils.misc import (derive_page, derive_section_root,
                                     get_site_from_request)


def wagtailmenus(request):

    def _get_wagtailmenus_vals():
        current_page = request.META.get('WAGTAILMENUS_CURRENT_PAGE')
        section_root = request.META.get('WAGTAILMENUS_CURRENT_SECTION_ROOT')
        site = get_site_from_request(request, fallback_to_default=True)
        ancestor_ids = ()
        match = None

        guess_position = settings.GUESS_TREE_POSITION_FROM_PATH
        section_root_depth = settings.SECTION_ROOT_DEPTH

        if guess_position and not current_page:
            match, full_url_match = derive_page(request, site)
            if full_url_match:
                current_page = match

        if not section_root and current_page or match:
            section_root = derive_section_root(current_page or match)

        if current_page or match:
            page = current_page or match
            if page.depth >= section_root_depth:
                ancestor_ids = page.get_ancestors(inclusive=True).filter(
                    depth__gte=section_root_depth).values_list('id', flat=True)

        return {
            'current_page': current_page,
            'section_root': section_root,
            'current_page_ancestor_ids': ancestor_ids,
        }

    return {
        'wagtailmenus_vals': SimpleLazyObject(_get_wagtailmenus_vals),
    }
