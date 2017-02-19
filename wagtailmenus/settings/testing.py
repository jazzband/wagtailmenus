from .base import *  # NOQA

DEBUG = False
SITE_ID = 1

DATABASES = {
    'default': {
        'NAME': 'wagtailmenus-testing.sqlite',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS += (
    'wagtailmenus.tests',
)

ROOT_URLCONF = 'wagtailmenus.tests.urls'
WAGTAIL_SITE_NAME = 'Wagtailmenus Test'
LOGIN_URL = 'wagtailadmin_login'
LOGIN_REDIRECT_URL = 'wagtailadmin_home'
