
.. _custom_menu_classes:

====================================
Using custom menu classes and models
====================================

.. contents::
    :local:
    :depth: 2


.. _custom_main_menu_models:

Overriding the models used for main menus
=========================================

There are a couple of different approaches for overriding the models used for defining / rendering main menus. The best approach for your project depends on which models you need to override.


Replacing the ``MainMenuItem`` model only
-----------------------------------------

If you're happy with the default ``MainMenu`` model, but wish customise the menu item model (e.g. to add images, description fields, or extra fields for translated strings), you can use the :ref:`MAIN_MENU_ITEMS_RELATED_NAME` setting to have main menus use a different model, both within Wagtail's CMS, and for generating the list of ``menu_items`` used by menu templates.

1.  Within your project, define your custom model by subclassing
    ``AbstractMainMenuItem``:

    .. code-block:: python

        # appname/models.py

        from django.db import models
        from django.utils.translation import ugettext_lazy as _
        from modelcluster.fields import ParentalKey
        from wagtail.images import get_image_model_string
        from wagtail.images.edit_handlers import ImageChooserPanel
        from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel
        from wagtailmenus.models import AbstractMainMenuItem


        class CustomMainMenuItem(AbstractMainMenuItem):
            """A custom menu item model to be used by ``wagtailmenus.MainMenu``"""

            menu = ParentalKey(
                'wagtailmenus.MainMenu',
                on_delete=models.CASCADE,
                related_name="custom_menu_items", # important for step 3!
            )
            image = models.ForeignKey(
                get_image_model_string(),
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
            )
            hover_description = models.CharField(
                max_length=250,
                blank=True
            )

            # Also override the panels attribute, so that the new fields appear
            # in the admin interface
            panels = (
                PageChooserPanel('link_page'),
                FieldPanel('link_url'),
                FieldPanel('url_append'),
                FieldPanel('link_text'),
                ImageChooserPanel('image'),
                FieldPanel('hover_description'),
                FieldPanel('allow_subnav'),
            )

2.  Create migrations for the new model by running:

    .. code-block:: console

        python manage.py makemigrations appname

3.  Apply the new migrations by running:

    .. code-block:: console

        python manage.py migrate appname

4.  Add a setting to your project to instruct wagtailmenus to use your custom
    model instead of the default:

    .. code-block:: python

        # Set this to the 'related_name' attribute used on the ParentalKey field
        WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME = "custom_menu_items"

5.  *That's it!* The custom models will now be used instead of the default ones.

    .. NOTE::
        Although you won't be able to see them in the CMS any longer, the default models and any data that was in the original database table will remain intact.


Replacing both the ``MainMenu`` and ``MainMenuItem`` models
-----------------------------------------------------------

If you also need to override the ``MainMenu`` model, that's possible too. But, because the ``MainMenuItem`` model is tied to ``MainMenu``, you'll also need to create custom menu item model (whether you wish to add fields / change their behaviour, or not).

1.  Within your project, define your custom models by subclassing the
    ``AbstractMainMenu`` and ``AbstractMainMenuItem`` model classes:

    .. code-block:: python

        # appname/models.py

        from django.db import models
        from django.utils import translation
        from django.utils.translation import ugettext_lazy as _
        from django.utils import timezone
        from modelcluster.fields import ParentalKey
        from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel
        from wagtailmenus.conf import settings
        from wagtailmenus.models import AbstractMainMenu, AbstractMainMenuItem


        class LimitedMainMenu(AbstractMainMenu):
            limit_from = models.TimeField()
            limit_to = models.TimeField()

            def get_base_page_queryset(self):
                """
                If the current time is between 'limit_from' and 'limit_to',
                only surface pages that are owned by the logged in user
                """
                if(
                    self.request.user and
                    self.limit_from < timezone.now() < self.limit_to
                ):

                    return self.request.user.owned_pages.filter(
                        live=True, expired=False, show_in_menus=True
                    )
                return Page.objects.none()

            # Like pages, panels for menus are split into multiple tabs.
            # To update the panels in the 'Content' tab, override 'content_panels'
            # To update the panels in the 'Settings' tab, override 'settings_panels'
            settings_panels = AbstractMainMenu.setting_panels += (
                MultiFieldPanel(
                    heading=_('Time limit settings'),
                    children=(
                        FieldPanel('limit_from'),
                        FieldPanel('limit_to'),
                    ),
                ),
            )

        class CustomMainMenuItem(AbstractMainMenuItem):
            """A minimal custom menu item model to be used by `LimitedMainMenu`.
            No additional fields / method necessary
            """
            menu = ParentalKey(
                LimitedMainMenu, # we can use the model from above
                on_delete=models.CASCADE,
                related_name=settings.MAIN_MENU_ITEMS_RELATED_NAME,
            )

2.  Create migrations for the new models by running:

    .. code-block:: console

        python manage.py makemigrations appname

3.  Apply the new migrations by running:

    .. code-block:: console

        python manage.py migrate appname

4.  Add a setting to your project to tell wagtailmenus to use your custom menu
    model instead of the default one. e.g:

    .. code-block:: python

        # e.g. settings/base.py

        WAGTAILMENUS_MAIN_MENU_MODEL = "appname.LimitedMainMenu"

5.  *That's it!* The custom models will now be used instead of the default ones.

    .. NOTE::
        Although you won't be able to see them in the CMS any longer, the default models and any data that was in the original database table will remain intact.


.. _custom_flat_menu_models:

Overriding the models used for flat menus
=========================================

There are a couple of different approaches for overriding the models used for defining / rendering flat menus. The best approach for your project depends on which models you need to override.

Replacing the ``FlatMenuItem`` model only
-----------------------------------------

If you're happy with the default ``FlatMenu`` model, but wish customise the menu item models (e.g. to add images, description fields, or extra fields for translated strings), you can use the :ref:`FLAT_MENU_ITEMS_RELATED_NAME` setting to have flat menus use a different model, both within Wagtail's CMS, and for generating the list of ``menu_items`` used by menu templates.

1.  Within your project, define your custom model by subclassing ``AbstractFlatMenuItem``:

    .. code-block:: python

        # apname/models.py

        from django.db import models
        from django.utils.translation import ugettext_lazy as _
        from modelcluster.fields import ParentalKey
        from wagtail.images import get_image_model_string
        from wagtail.images.edit_handlers import ImageChooserPanel
        from wagtail.admin.edit_handlers import FieldPanel, PageChooserPanel
        from wagtailmenus.models import AbstractFlatMenuItem


        class CustomFlatMenuItem(AbstractFlatMenuItem):
            """A custom menu item model to be used by ``wagtailmenus.FlatMenu``"""

            menu = ParentalKey(
                'wagtailmenus.FlatMenu',
                on_delete=models.CASCADE,
                related_name="custom_menu_items", # important for step 3!
            )
            image = models.ForeignKey(
                get_image_model_string(),
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
            )
            hover_description = models.CharField(
                max_length=250,
                blank=True
            )

            # Also override the panels attribute, so that the new fields appear
            # in the admin interface
            panels = (
                PageChooserPanel('link_page'),
                FieldPanel('link_url'),
                FieldPanel('url_append'),
                FieldPanel('link_text'),
                ImageChooserPanel('image'),
                FieldPanel('hover_description'),
                FieldPanel('allow_subnav'),
            )

2.  Create migrations for the new models by running:

    .. code-block:: console

        python manage.py makemigrations appname

3.  Apply the new migrations by running:

    .. code-block:: console

        python manage.py migrate appname

4.  Add a setting to your project to tell wagtailmenus to use your custom model
    instead of the default one. e.g:

    .. code-block:: python

        # e.g. settings/base.py

        # Use the 'related_name' attribute you used on your custom model's ParentalKey field
        WAGTAILMENUS_FLAT_MENU_ITEMS_RELATED_NAME = "custom_menu_items"

5.  *That's it!* The custom models will now be used instead of the default ones.

    .. NOTE::
        Although you won't be able to see them in the CMS any longer, the default models and any data that was in the original database table will remain intact.


Replacing both the ``FlatMenu`` and ``FlatMenuItem`` models
-----------------------------------------------------------

If you also need to override the ``FlatMenu`` model, that's possible too. But, because the ``FlatMenuItem`` model is tied to ``FlatMenu``, you'll also need to create custom menu item model (whether you wish to add fields or their behaviour or not).

1.  Within your project, define your custom models by subclassing the
    ``AbstractFlatMenu`` and ``AbstractFlatMenuItem`` model classes:

    .. code-block:: python

        # appname/models.py

        from django.db import models
        from django.utils import translation
        from django.utils.translation import ugettext_lazy as _
        from modelcluster.fields import ParentalKey
        from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel
        from wagtailmenus.conf import settings
        from wagtailmenus.panels import FlatMenuItemsInlinePanel
        from wagtailmenus.models import AbstractFlatMenu, AbstractFlatMenuItem


        class TranslatedField(object):
            """
            A class that can be used on models to return a 'field' in the
            desired language, where there a multiple versions of a field to
            cater for multiple languages (in this case, English, German & French)
            """
            def __init__(self, en_field, de_field, fr_field):
                self.en_field = en_field
                self.de_field = de_field
                self.fr_field = fr_field

            def __get__(self, instance, owner):
                active_language = translation.get_language()
                if active_language == 'de':
                    return getattr(instance, self.de_field)
                if active_language == 'fr':
                    return getattr(instance, self.fr_field)
                return getattr(instance, self.en_field)


        class TranslatedFlatMenu(AbstractFlatMenu):
            heading_de = models.CharField(
                verbose_name=_("heading (german)"),
                max_length=255,
                blank=True,
            )
            heading_fr = models.CharField(
                verbose_name=_("heading (french)"),
                max_length=255,
                blank=True,
            )
            translated_heading = TranslatedField('heading', 'heading_de', 'heading_fr')

            # Like pages, panels for menus are split into multiple tabs.
            # To update the panels in the 'Content' tab, override 'content_panels'
            # To update the panels in the 'Settings' tab, override 'settings_panels'
            content_panels = (
                MultiFieldPanel(
                    heading=_("Settings"),
                    children=(
                        FieldPanel("title"),
                        FieldPanel("site"),
                        FieldPanel("handle"),
                    )
                ),
                MultiFieldPanel(
                    heading=_("Heading"),
                    children=(
                        FieldPanel("heading"),
                        FieldPanel("heading_de"),
                        FieldPanel("heading_fr"),
                    ),
                    classname='collapsible'
                ),
                FlatMenuItemsInlinePanel(),
            )

        class TranslatedFlatMenuItem(AbstractFlatMenuItem):
            """A custom menu item model to be used by ``TranslatedFlatMenu``"""

            menu = ParentalKey(
                TranslatedFlatMenu, # we can use the model from above
                on_delete=models.CASCADE,
                related_name=settings.FLAT_MENU_ITEMS_RELATED_NAME,
            )
            link_text_de = models.CharField(
                verbose_name=_("link text (german)"),
                max_length=255,
                blank=True,
            )
            link_text_fr = models.CharField(
                verbose_name=_("link text (french)"),
                max_length=255,
                blank=True,
            )
            translated_link_text = TranslatedField('link_text', 'link_text_de', 'link_text_fr')

            @property
            def menu_text(self):
                """Use `translated_link_text` instead of just `link_text`"""
                return self.translated_link_text or getattr(
                    self.link_page,
                    settings.PAGE_FIELD_FOR_MENU_ITEM_TEXT,
                    self.link_page.title
                )

            # Also override the panels attribute, so that the new fields appear
            # in the admin interface
            panels = (
                PageChooserPanel("link_page"),
                FieldPanel("link_url"),
                FieldPanel("url_append"),
                FieldPanel("link_text"),
                FieldPanel("link_text_de"),
                FieldPanel("link_text_fr"),
                FieldPanel("handle"),
                FieldPanel("allow_subnav"),
            )

2.  Create migrations for the new models by running:

    .. code-block:: console

        python manage.py makemigrations appname

3.  Apply the new migrations by running:

    .. code-block:: console

        python manage.py migrate appname

4.  Add a setting to your project to tell wagtailmenus to use your custom
    menu model instead of the default one. e.g:

    .. code-block:: python

        # e.g. settings/base.py

        WAGTAILMENUS_FLAT_MENU_MODEL = "appname.TranslatedFlatMenu"

5.  That's it! The custom models will now be used instead of the default ones.

    .. NOTE::
        Although you won't be able to see them in the CMS any longer, the
        default models and any data that was in the original database table
        will remain intact.


.. _custom_sectionmenu_class:

Overriding the menu class used by ``{% section_menu %}``
========================================================

Like the ``main_menu`` and ``flat_menu`` tags, the ``section_menu`` tag uses a ``Menu`` class to fetch all of the data needed to render a menu. Though, because section menus are driven entirely by your existing page tree (and don't need to store any additional data), it's just a plain old Python class and not a Django model.

The class ``wagtailmenus.models.menus.SectionMenu`` is used by default, but you can use the ``WAGTAILMENUS_SECTION_MENU_CLASS`` setting in your project to make wagtailmenus use an alternative class (for example, if you want to modify the base queryset that determines which pages should be included when rendering). To implement a custom classes, it's recommended that you subclass the ``SectionMenu`` and override any methods as required, like in the following example:

.. code-block:: python

    # mysite/appname/models.py

    from django.utils.translation import ugettext_lazy as _
    from wagtail.core.models import Page
    from wagtailmenus.models import SectionMenu


    class CustomSectionMenu(SectionMenu):

        def get_base_page_queryset(self):
            # Show draft and expired pages in menu for superusers
            if self.request.user.is_superuser:
                return Page.objects.filter(show_in_menus=True)
            # Resort to default behaviour for everybody else
            return super(CustomSectionMenu, self).get_base_page_queryset()


.. code-block:: python

    # e.g. settings/base.py

    WAGTAILMENUS_SECTION_MENU_CLASS = "mysite.appname.models.CustomSectionMenu"


.. _custom_childrenmenu_class:

Overriding the menu class used by ``{% children_menu %}``
=========================================================

Like all of the other tags, the ``children_menu`` tag uses a ``Menu`` class to fetch all of the data needed to render a menu. Though, because children menus are driven entirely by your existing page tree (and do not need to store any additional data), it's just a plain old Python class and not a Django model.

The class ``wagtailmenus.models.menus.ChildrenMenu`` is used by default, but you can use the ``WAGTAILMENUS_CHILDREN_MENU_CLASS`` setting in your project to make wagtailmenus use an alternative class (for example, if you want to modify which pages are included). For custom classes, it's recommended that you subclass ``ChildrenMenu`` and override any methods as required e.g:

.. code-block:: python

    # appname/menus.py

    from django.utils.translation import ugettext_lazy as _
    from wagtail.core.models import Page
    from wagtailmenus.models import ChildrenMenu


    class CustomChildrenMenu(ChildrenMenu):
        def get_base_page_queryset(self):
        # Show draft and expired pages in menu for superusers
        if self.request.user.is_superuser:
            return Page.objects.filter(show_in_menus=True)
        # Resort to default behaviour for everybody else
        return super(CustomChildrenMenu, self).get_base_page_queryset()


.. code-block:: python

    # e.g. settings/base.py

    WAGTAILMENUS_CHILDREN_MENU_CLASS = "mysite.appname.models.CustomChildrenMenu"

