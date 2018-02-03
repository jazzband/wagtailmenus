from django.conf.urls import include, url
from django.views.generic import TemplateView
from wagtail import VERSION as WAGTAIL_VERSION
if WAGTAIL_VERSION >= (2, 0):
    from wagtail.admin import urls as wagtailadmin_urls
    from wagtail.core import urls as wagtail_urls
else:
    from wagtail.wagtailadmin import urls as wagtailadmin_urls
    from wagtail.wagtailcore import urls as wagtail_urls


urlpatterns = [
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^custom-url/$', TemplateView.as_view(template_name='page.html')),
    url(r'^sub_menu-tag-used-directly/$',
        TemplateView.as_view(template_name='sub_menu-tag-used-directly.html')),
    url(r'^superheroes/marvel-comics/custom-man/about/$',
        TemplateView.as_view(template_name='page.html')),
    url(r'^about-us/meet-the-team/staff-member-one/$',
        TemplateView.as_view(template_name='page.html')),
    url(r'^about-us/meet-the-team/custom-url/$',
        TemplateView.as_view(template_name='page.html')),
    url(r'^news-and-events/$',
        TemplateView.as_view(template_name='page.html')),
    # Hijacking the iron-man page to render a different template, that tests
    # the effect of `use_specific=0` in template tags
    url(r'^superheroes/marvel-comics/iron-man/$',
        TemplateView.as_view(template_name='use-specific-off.html')),
    # Hijacking the batman page to render a different template, that tests
    # the effect of `use_specific=2` in template tags
    url(r'^superheroes/dc-comics/batman/$',
        TemplateView.as_view(template_name='use-specific-top-level.html')),
    # Hijacking the wonder-woman page to render to different template, that
    # tests the effect of `use_specific=3` in template tags
    url(r'^superheroes/dc-comics/wonder-woman/$',
        TemplateView.as_view(template_name='use-specific-always.html')),
    url(r'', include(wagtail_urls)),
]
