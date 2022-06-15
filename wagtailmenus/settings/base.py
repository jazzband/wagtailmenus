import os

DEBUG = True
SITE_ID = 1

TIME_ZONE = 'Europe/London'
USE_TZ = True
USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = 'en'


INSTALLED_APPS = (
    'wagtailmenus',

    'taggit',
    'modelcluster',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'wagtail.admin',
    'wagtail.core',
    'wagtail.documents',
    'wagtail.embeds',
    'wagtail.images',
    'wagtail.sites',
    'wagtail.search',
    'wagtail.snippets',
    'wagtail.users',
    'wagtail.contrib.redirects',
    'wagtail.contrib.routable_page',
    'wagtail.contrib.settings',
    'wagtail.contrib.modeladmin',

)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'

SECRET_KEY = 'fake-key'
LOGIN_URL = 'wagtailadmin_login'
LOGIN_REDIRECT_URL = 'wagtailadmin_home'

LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'locale'),
)

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
                'wagtailmenus.context_processors.wagtailmenus'
            ],
        },
    },
]

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

WAGTAILMENUS_FLAT_MENUS_HANDLE_CHOICES = (
    ('contact', 'contact'),
    ('footer', 'footer'),
    ('header-secondary', 'header-secondary'),
)
