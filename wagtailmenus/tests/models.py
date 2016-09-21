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
