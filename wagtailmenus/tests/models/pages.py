from datetime import date

from django.db import models
from django.http import Http404
from django.template.response import TemplateResponse
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PublishingPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.models import Page

from wagtailmenus.models import AbstractLinkPage, MenuPage

from .utils import TranslatedField


class MultilingualMenuPage(MenuPage):
    title_de = models.CharField(
        verbose_name='title (de)',
        blank=True,
        max_length=255,
    )
    title_fr = models.CharField(
        verbose_name='title (fr)',
        blank=True,
        max_length=255,
    )
    repeated_item_text_de = models.CharField(
        verbose_name='repeated item link text (de)',
        blank=True,
        max_length=255,
    )
    repeated_item_text_fr = models.CharField(
        verbose_name='repeated item link text (fr)',
        blank=True,
        max_length=255,
    )
    translated_title = TranslatedField(
        'title', 'title_de', 'title_fr'
    )
    translated_repeated_item_text = TranslatedField(
        'repeated_item_text', 'repeated_item_text_de', 'repeated_item_text_fr',
    )

    class Meta:
        abstract = True

    def modify_submenu_items(
        self, menu_items, current_page, current_ancestor_ids,
        current_site, allow_repeating_parents, apply_active_classes,
        original_menu_tag, menu_instance, request, use_absolute_page_urls
    ):
        return super().modify_submenu_items(
            menu_items, current_page, current_ancestor_ids,
            current_site, allow_repeating_parents, apply_active_classes,
            original_menu_tag, menu_instance, request, use_absolute_page_urls)

    def has_submenu_items(
        self, current_page, allow_repeating_parents, original_menu_tag,
        menu_instance, request
    ):
        return super().has_submenu_items(
            current_page, allow_repeating_parents, original_menu_tag,
            menu_instance, request)

    def get_repeated_menu_item(
        self, current_page, current_site, apply_active_classes,
        original_menu_tag, request, use_absolute_page_urls
    ):
        item = super().get_repeated_menu_item(
            current_page, current_site, apply_active_classes,
            original_menu_tag, request, use_absolute_page_urls)
        item.text = self.translated_repeated_item_text or self.translated_title
        return item

    settings_panels = [
        PublishingPanel(),
        MultiFieldPanel(
            heading="Advanced menu behaviour",
            classname="collapsible collapsed",
            children=(
                FieldPanel('repeat_in_subnav'),
                FieldPanel('repeated_item_text'),
                FieldPanel('repeated_item_text_de'),
                FieldPanel('repeated_item_text_fr'),
            )
        )
    ]


class HomePage(MenuPage):
    template = 'homepage.html'
    parent_page_types = [Page]


class TopLevelPage(MultilingualMenuPage):
    template = 'page.html'
    parent_page_types = [HomePage]


class LowLevelPage(Page):
    template = 'page.html'


class TypicalPage(Page):
    template = 'typical-page.html'


class ContactPage(MenuPage):
    template = 'page.html'
    parent_page_types = [HomePage]
    subpage_types = []

    def modify_submenu_items(
        self, menu_items, current_page, current_ancestor_ids,
        current_site, allow_repeating_parents, apply_active_classes,
        original_menu_tag, menu_instance=None, request=None, use_absolute_page_urls=False
    ):
        menu_items = super().modify_submenu_items(
            menu_items, current_page, current_ancestor_ids,
            current_site, allow_repeating_parents, apply_active_classes,
            original_menu_tag, menu_instance, use_absolute_page_urls=use_absolute_page_urls)
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

    def has_submenu_items(
        self, current_page, allow_repeating_parents,
        original_menu_tag, menu_instance=None, request=None
    ):
        """
        Because `modify_submenu_items` is being used to add additional menu
        items, we need to indicate in menu templates that `ContactPage` objects
        do have submenu items in main menus, even if they don't have children
        pages.
        """
        if original_menu_tag == 'main_menu':
            return True
        return super().has_submenu_items(
            current_page, allow_repeating_parents, original_menu_tag,
            menu_instance, request)


class NoAbsoluteUrlsPage(MenuPage):
    """
    Ensure that we can handle pages that do not specify the `use_absolute_page_urls` kwarg.
    """

    template = 'page.html'
    parent_page_types = [HomePage]

    def modify_submenu_items(
        self, menu_items, current_page, current_ancestor_ids,
        current_site, allow_repeating_parents, apply_active_classes,
        original_menu_tag, menu_instance=None, request=None
    ):
        return super().modify_submenu_items(
            menu_items, current_page, current_ancestor_ids,
            current_site, allow_repeating_parents, apply_active_classes,
            original_menu_tag, menu_instance, request)

    def get_repeated_menu_item(
        self, current_page, current_site, apply_active_classes,
        original_menu_tag, request
    ):
        return super().get_repeated_menu_item(
            current_page, current_site, apply_active_classes,
            original_menu_tag, request
        )


class LinkPage(AbstractLinkPage):
    pass


class ArticleListPage(RoutablePageMixin, Page):
    template = 'page.html'
    subpage_types = ['tests.ArticlePage']

    def render(self, request, **kwargs):
        return TemplateResponse(
            request,
            self.get_template(request, **kwargs),
            self.get_context(request, **kwargs)
        )

    @route(r'^$')
    def default_view(self, request):
        """
        List published aticles
        """
        return self.render(request)

    @route(r'^([0-9]{4})/$')
    def year_view(self, request, year):
        """
        List articles published within a specific year
        """
        return self.render(request, year=year)

    @route(r'^([0-9]{4})/([0-9]{2})/$')
    def month_view(self, request, year, month):
        """
        List articles published within a specific month
        """
        return self.render(request, year=year, month=month)

    @route(r'^([0-9]{4})/([0-9]{2})/([0-9]{2})/$')
    def day_view(self, request, year, month, day):
        """
        List articles published on a specific day
        """
        return self.render(request, year=year, month=month, day=day)

    def route(self, request, path_components):
        """
        Overrides RoutablePageMixin.route() to allow articles to have
        publish date components in URLs."""

        if len(path_components) >= 4:

            # Attempt to route to an article using date/slug components
            # NOTE: The page must have been published in order for
            # `first_published_at` to be set
            try:
                year = path_components[0]  # year
                month = path_components[1]  # month
                day = path_components[2]  # day
                slug = path_components[3]  # slug
                publish_date = date(int(year), int(month), int(day))
            except ValueError:
                # Date components invalid
                raise Http404

            try:
                # Find an article matching the above date and slug
                article = ArticlePage.objects.child_of(self).get(
                    publish_date=publish_date, slug=slug)
            except ArticlePage.DoesNotExist:
                raise Http404

            # Delegate further routing to the arcicle, excluding the
            # date and slug components used above
            return article.route(request, path_components[4:])

        return super().route(request, path_components)


class ArticlePage(Page):
    template = 'page.html'
    parent_page_types = ['tests.ArticleListPage']

    publish_date = models.DateField()

    content_panels = Page.content_panels + [
        FieldPanel('publish_date')
    ]

    def get_url_parts(self, request=None):
        """
        Overrides Page.get_url_parts() to replace the 'page path'
        part, so that article urls include segments for the
        article's `publish_date` as well as the `slug`
        """
        site_id, root_url, page_path = super().get_url_parts(request)

        page_path_bits = page_path.rstrip('/').split('/')
        slug = page_path_bits.pop()

        page_path_bits.extend(
            self.publish_date.strftime('%Y|%m|%d').split('|')
        )

        # Add the slug to the end and re-combine
        page_path_bits.append(slug)
        page_path = '/'.join(page_path_bits) + '/'
        return site_id, root_url, page_path
