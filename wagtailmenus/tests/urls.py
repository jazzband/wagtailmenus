from django.conf.urls import include
from django.urls import re_path
from django.views.generic import TemplateView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls

urlpatterns = [
    re_path(r'^admin/', include(wagtailadmin_urls)),
    re_path(r'^custom-url/$', TemplateView.as_view(template_name='page.html')),
    re_path(r'^sub_menu-tag-used-directly/$',
        TemplateView.as_view(template_name='sub_menu-tag-used-directly.html')),
    re_path(r'^superheroes/marvel-comics/custom-man/about/$',
        TemplateView.as_view(template_name='page.html')),
    re_path(r'^about-us/meet-the-team/staff-member-one/$',
        TemplateView.as_view(template_name='page.html')),
    re_path(r'^about-us/meet-the-team/custom-url/$',
        TemplateView.as_view(template_name='page.html')),
    re_path(r'^news-and-events/$',
        TemplateView.as_view(template_name='page.html')),
    re_path(r'', include(wagtail_urls)),
]
