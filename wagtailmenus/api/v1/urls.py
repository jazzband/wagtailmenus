from django.conf.urls import url
from . import views

app_name = 'v1'

urlpatterns = [
    url(r'^$', views.MenuGeneratorIndexView.as_view(), name="index"),
    url(r'^main_menu/$', views.MainMenuGeneratorView.as_view(), name="main_menu"),
    url(r'^flat_menu/$', views.FlatMenuGeneratorView.as_view(), name="flat_menu"),
    url(r'^children_menu/$', views.ChildrenMenuGeneratorView.as_view(), name="children_menu"),
    url(r'^section_menu/$', views.SectionMenuGeneratorView.as_view(), name="section_menu"),
]
