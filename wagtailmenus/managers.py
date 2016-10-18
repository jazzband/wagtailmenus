from django.db import models


class MenuItemManager(models.Manager):
    ''' App-specific manager overrides '''

    def for_display(self):
        return self.filter(
            models.Q(link_page__isnull=True) |
            models.Q(link_page__live=True) &
            models.Q(link_page__expired=False) &
            models.Q(link_page__show_in_menus=True)
        )

    def page_links(self):
        return self.filter(link_page__isnull=False)

    def page_links_for_display(self):
        return self.page_links().filter(
            link_page__live=True,
            link_page__expired=False,
            link_page__show_in_menus=True)
