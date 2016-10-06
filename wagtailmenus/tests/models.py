from wagtail.wagtailcore.models import Page
from wagtailmenus.models import MenuPage


class HomePage(MenuPage):
    template = 'homepage.html'
    parent_page_types = [Page]


class TopLevelPage(MenuPage):
    extra_menuitem_css_class = 'top-level'
    template = 'page.html'
    parent_page_types = [HomePage]


class LowLevelPage(Page):
    extra_menuitem_css_class = 'low-level'
    template = 'page.html'


class ContactPage(MenuPage):
    template = 'page.html'
    parent_page_types = [HomePage]
    subpage_types = []

    def modify_submenu_items(self, menu_items, current_page,
                             current_ancestor_ids, current_site,
                             allow_repeating_parents, apply_active_classes,
                             original_menu_tag):
        menu_items = super(ContactPage, self).modify_submenu_items(
            menu_items, current_page, current_ancestor_ids, current_site,
            allow_repeating_parents, apply_active_classes, original_menu_tag)
        """
        If rendering a 'main_menu', add some additional menu items to the end
        of the list that link to various anchored sections on the same page
        """
        if original_menu_tag == 'main_menu':
            base_url = self.relative_url(current_site)
            menu_items.extend((
                {
                    'text': 'Get support',
                    'href': base_url + '#support',
                    'active_class': 'support',
                },
                {
                    'text': 'Speak to someone',
                    'href': base_url + '#call',
                    'active_class': 'call',
                },
                {
                    'text': 'Map & directions',
                    'href': base_url + '#map',
                    'active_class': 'map',
                },
            ))
        return menu_items

    def has_submenu_items(self, current_page, check_for_children,
                          allow_repeating_parents, original_menu_tag):
        """
        Because `modify_submenu_items` is being used to add additional menu
        items, we need to indicate in menu templates that `ContactPage` objects
        do have submenu items in main menus, even if they don't have children
        pages.
        """
        if original_menu_tag == 'main_menu':
            return True
        return super(ContactPage, self).has_submenu_items(
            current_page, check_for_children, allow_repeating_parents,
            original_menu_tag)
