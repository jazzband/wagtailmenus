.. _installing_wagtailmenus:

=========================
Installing wagtailmenus
=========================

1.  Install the package using pip:

    .. code-block:: console

        pip install wagtailmenus

2.  Add ``wagtailmenus`` and ``wagtail.contrib.modeladmin`` to the
    ``INSTALLED_APPS`` setting in your project settings:

    .. code-block:: python
        :caption: e.g. settings/base.py

        INSTALLED_APPS = [
            ...
            'wagtail.contrib.modeladmin',  # Don't repeat if it's there already
            'wagtailmenus',
        ]

3.  Add ``wagtailmenus.context_processors.wagtailmenus`` to the
    ``context_processors`` list in your ``TEMPLATES`` setting. The setting
    should look something like this:

    .. code-block:: python
        :caption: e.g. settings/base.py
        :emphasize-lines: 19

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

5.  **This step is optional**. If you're adding wagtailmenus to an existing
    project, and the tree for each site follows a structure similar to the
    example below, you may find it useful to run the 'autopopulate_main_menus'
    command to populate main menus for your site(s).

    However, this will only yield useful results if the 'root page' you've
    set for your site(s) is what you consider to be the 'Home' page, and the
    pages directly below that are the pages you'd like to link to in your main
    menu.

    For example, if your page structure looked like the following:

    .. code-block:: none

        Home (Set as 'root page' for the site)
        ├── About us
        ├── What we do
        ├── Careers
        │   ├── Vacancy one
        │   └── Vacancy two
        ├── News & events
        │   ├── News
        │   └── Events
        └── Contact us

    Running the command from the console:

    .. code-block:: console

        python manage.py autopopulate_main_menus

    Would create a main menu with the following items:

    * About us
    * What we do
    * Careers
    * News & events
    * Contact us

    If you'd like wagtailmenus to also include a link to the 'home page', you
    can use the '--add-home-links' option, like so:

    .. code-block:: console

        python manage.py autopopulate_main_menus --add-home-links=True

    This would create a main menu with the following items:

    * Home
    * About us
    * What we do
    * Careers
    * News & events
    * Contact us

    .. note ::
        The 'autopopulate_main_menus' command is meant as 'run once' command to
        help you get started, and will only affect menus that do not already
        have any menu items defined. Running it more than once won't have any
        effect, even if you make changes to your page tree before running it
        again.
