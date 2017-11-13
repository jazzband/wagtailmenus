.. _use_with_jinja2:

===============================
Use with Jinja2 template engine
===============================


If your project uses `Jinja2 <http://jinja.pocoo.org>`_ for template, the template for *wagtailmenus* has also be written in Jinja2. Assume that your source folder tree is like this::

    + project
    |  +-- settings.py
    |  +-- urls.py
    + templates
    |  +-- base.jinja
    |  +-- menus
    + manage.py


Here is how to make wagtailmenus work with Jinja2:

1. Create *jinja.py* file:

.. code-block:: python

    import jinja2
    from jinja2 import Environment
    from jinja2.ext import Extension
    from django.conf import settings
    from wagtailmenus.templatetags.menu_tags import main_menu, sub_menu


    def environment(**options):
        env = Environment(**options)
        env.globals.update({
            'settings': settings,
        })
        return env


    class MenuExtension(Extension):
        def __init__(self, environment):
            super().__init__(environment)
            environment.globals.update({
                'main_menu': jinja2.contextfunction(main_menu),
                'sub_menu': jinja2.contextfunction(sub_menu),
            })


2. Setup ``TEMPLATES`` in *settings.py* (not complete):

.. code-block:: python

    from django_jinja.builtins import DEFAULT_EXTENSIONS

    TEMPLATES = (
        {
            'NAME': 'django-jinja',
            'BACKEND': 'django_jinja.backend.Jinja2',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],
            'APP_DIRS': True,
            'OPTIONS': {
                'environment': 'project.jinja.environment',
                'match_extension': '.jinja',
                'extensions': DEFAULT_EXTENSIONS + [
                    'wagtail.wagtailcore.jinja2tags.core',
                    'wagtail.wagtailadmin.jinja2tags.userbar',
                    'wagtail.wagtailimages.jinja2tags.images',
                    # My extension for wagtailmenus
                    'project.jinja.MenuExtension',
                ],
            }
        },
    )


Here in my example, I use `django-jinja <https://github.com/niwinz/django-jinja>`_ for integrating Jinja2 with Django. My convention is that template files are named with ".jinja" and put in *templates* folder.

3. Write your Jinja2 template for menu and change ``WAGTAILMENUS_DEFAULT_MAIN_MENU_TEMPLATE`` setting.

.. code-block:: python

    WAGTAILMENUS_DEFAULT_MAIN_MENU_TEMPLATE = 'menus/main_menu.jinja'
    WAGTAILMENUS_DEFAULT_SUB_MENU_TEMPLATE = 'menus/sub_menu.jinja'


4. In your template content, insert menu like this:

.. code-block:: jinja

    <div class="collapse navbar-collapse" id="myNavbar">
      {{ main_menu() }}
    </div>


