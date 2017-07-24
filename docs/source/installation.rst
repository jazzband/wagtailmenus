.. _installing_wagtailmenus:

=========================
Installating wagtailmenus
=========================

1.  Install the package using pip: 

    .. code-block:: console

        pip install wagtailmenus

2.  Add ``wagtailmenus`` and ``wagtail.contrib.modeladmin`` to the
    ``INSTALLED_APPS`` setting in your project settings:

    .. code-block:: python

        INSTALLED_APPS = [
            ...
            'wagtail.contrib.modeladmin',  # Don't repeat if it's there already
            'wagtailmenus',
        ]

3.  Add ``wagtailmenus.context_processors.wagtailmenus`` to the 
    ``context_processors`` list in your ``TEMPLATES`` setting. The setting 
    should look something like this:
    
    .. code-block:: python

        TEMPLATES = [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                '   DIRS': [
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
                        'wagtailmenus.context_processors.wagtailmenus',
                    ],
                },
            },
        ]

4.  Run migrations to create database tables for wagtailmenus:
    
    .. code-block:: console

        python manage.py migrate wagtailmenus
