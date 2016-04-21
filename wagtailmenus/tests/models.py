from wagtail.wagtailcore.models import Page
from wagtailmenus.models import MenuPage


class HomePage(MenuPage):
    template = 'homepage.html'
    parent_page_types = [Page]


class TopLevelPage(MenuPage):
    template = 'page.html'
    parent_page_types = [HomePage]


class LowLevelPage(Page):
    template = 'page.html'
