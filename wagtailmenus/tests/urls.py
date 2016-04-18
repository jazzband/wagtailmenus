from django.conf import settings
from django.conf.urls import include, url

from django.views.generic import TemplateView
from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtail_urls

urlpatterns = [
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^custom-url/$', TemplateView.as_view(template_name='page.html')),
    url(r'', include(wagtail_urls)),
]
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
