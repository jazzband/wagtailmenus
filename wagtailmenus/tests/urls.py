from django.conf.urls import include
from django.urls import path
from django.views.generic import TemplateView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls

urlpatterns = [
    path('admin/', include(wagtailadmin_urls)),
    path('custom-url/', TemplateView.as_view(template_name='page.html')),
    path('sub_menu-tag-used-directly/',
         TemplateView.as_view(template_name='sub_menu-tag-used-directly.html')),
    path('superheroes/marvel-comics/custom-man/about/',
         TemplateView.as_view(template_name='page.html')),
    path('about-us/meet-the-team/staff-member-one/',
         TemplateView.as_view(template_name='page.html')),
    path('about-us/meet-the-team/custom-url/',
         TemplateView.as_view(template_name='page.html')),
    path('news-and-events/',
         TemplateView.as_view(template_name='page.html')),
    path('', include(wagtail_urls)),
]
