from django.conf.urls import include, url

from django.views.generic import TemplateView
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtail_urls

urlpatterns = [
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^custom-url/$', TemplateView.as_view(template_name='page.html')),
    url(r'', include(wagtail_urls)),
]
