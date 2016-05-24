import os
from django.conf.global_settings import *  # NOQA

DEBUG = True
SITE_ID = 1

DATABASES = {
    'default': {
        'NAME': 'wagtailmenus.sqlite',
        'TEST_NAME': 'wagtailmenus_test.sqlite',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

TIME_ZONE = 'Europe/London'
USE_TZ = True
USE_I18N = True
USE_L10N = True

INSTALLED_APPS = (
    'wagtailmenus.tests',
    'wagtailmenus',

    'wagtail.contrib.settings',
    'wagtail.wagtailforms',
    'wagtail.wagtailsearch',
    'wagtail.wagtailembeds',
    'wagtail.wagtailimages',
    'wagtail.wagtailsites',
    'wagtail.wagtailusers',
    'wagtail.wagtailsnippets',
    'wagtail.wagtaildocs',
    'wagtail.wagtailredirects',
    'wagtail.wagtailadmin',
    'wagtail.api',
    'wagtail.wagtailcore',
    'wagtail.contrib.modeladmin',

    'taggit',
    'modelcluster',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites'
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'test-static')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'test-media')
MEDIA_URL = '/media/'

SECRET_KEY = 'fake-key'

ROOT_URLCONF = 'wagtailmenus.tests.urls'

WAGTAIL_SITE_NAME = 'Test site'
LOGIN_URL = 'wagtailadmin_login'
LOGIN_REDIRECT_URL = 'wagtailadmin_home'


# =============================================================================
# Templates
# =============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_ROOT, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'wagtail.contrib.settings.context_processors.settings',
            ],
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.wagtailcore.middleware.SiteMiddleware',
    'wagtail.wagtailredirects.middleware.RedirectMiddleware',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
