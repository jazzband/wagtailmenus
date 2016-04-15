from wagtail.wagtailcore.models import Page
from wagtailmenus.models import MenuPage


class TopLevelPage(MenuPage):
    template = 'page.html'
    parent_page_types = [Page]
    subpage_types = [LowLevelPage]


class LowLevelPage(Page):
    template = 'page.html'
