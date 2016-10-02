from django.conf import settings
from django.conf.urls import include, url
from wagtailmenus.tests import urls as test_urls

urlpatterns = []
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
urlpatterns += [
    url(r'', include(test_urls)),
]
