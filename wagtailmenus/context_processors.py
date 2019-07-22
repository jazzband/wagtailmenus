from django.http import Http404
from django.utils.functional import SimpleLazyObject
from wagtailmenus.conf import settings
from wagtailmenus.utils.misc import get_site_from_request, get_page_from_request


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
            match, full_url_match = get_page_from_request(request, site, accept_best_match=True)
            if full_url_match:
                current_page = match

        if guess_position and not section_root:
            best_match = current_page or match
            if best_match:
                if best_match.depth == section_root_depth:
                    section_root = best_match
                elif best_match.depth > section_root_depth:
                    section_root = best_match.get_ancestors().filter(
                        depth__exact=section_root_depth).first()

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
