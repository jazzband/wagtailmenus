from django.conf.urls import include, url

app_name = 'wagtailmenus_api'
urlpatterns = [
    url(r'^v1/', include('wagtailmenus.api.v1.urls', namespace='v1')),
]
