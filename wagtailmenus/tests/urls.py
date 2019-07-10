from django.conf.urls import include, url
from django.views.generic import TemplateView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls


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
    url(r'', include(wagtail_urls)),
]
