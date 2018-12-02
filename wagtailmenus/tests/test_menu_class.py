from django.template import Context

from wagtailmenus.models import MainMenu
from wagtailmenus.tests import utils
from wagtailmenus.tests.test_mainmenu_class import MainMenuTestCase


class TestCreateDictFromParentContext(MainMenuTestCase):

    # ------------------------------------------------------------------------
    # Menu.create_dict_from_parent_context()
    # ------------------------------------------------------------------------

    def get_render_ready_menu_instance(self, parent_context=None):
        menu = MainMenu.objects.get(pk=1)
        ctx_vals = utils.make_contextualvals_instance(parent_context=parent_context)
        opt_vals = utils.make_optionvals_instance()
        menu.prepare_to_render(ctx_vals.request, ctx_vals, opt_vals)
        return menu

    def test_flattens_context_if_parent_context_is_django_template_context(self):
        menu = self.get_render_ready_menu_instance()
        template_context = menu._contextual_vals.parent_context

        result = menu.create_dict_from_parent_context()
        self.assertIsNot(result, template_context)
        self.assertEqual(result, template_context.flatten())

    def test_copies_value_if_parent_context_is_dict(self):
        dict_context = {'blah': 'blah'}
        menu = self.get_render_ready_menu_instance(parent_context=dict_context)

        result = menu.create_dict_from_parent_context()
        self.assertIsNot(result, dict_context)
        self.assertEqual(result, dict_context)

    def test_returns_empty_dict_if_partent_context_is_some_other_value_type(self):
        simple_context = Context({'blah': 'blah'})
        menu = self.get_render_ready_menu_instance(parent_context=simple_context)

        result = menu.create_dict_from_parent_context()
        self.assertIsNot(result, simple_context)
        self.assertIsInstance(result, dict)


class TestGetMenuItemsForRendering(MainMenuTestCase):

    # ------------------------------------------------------------------------
    # Menu.get_menu_items_for_rendering()
    # ------------------------------------------------------------------------

    def get_render_ready_menu_instance(self, **option_vals):
        menu = MainMenu.objects.get(pk=1)
        ctx_vals = utils.make_contextualvals_instance()
        opt_vals = utils.make_optionvals_instance(**option_vals)
        menu.prepare_to_render(ctx_vals.request, ctx_vals, opt_vals)
        return menu

    def test_sub_menu_items_not_added_inline_by_default(self):
        menu = self.get_render_ready_menu_instance()
        items_with_children = tuple(
            item for item in menu.get_menu_items_for_rendering()
            if getattr(item, 'has_children_in_menu', False)
        )
        self.assertGreater(len(items_with_children), 1)
        for menu_item in items_with_children:
            self.assertIs(getattr(menu_item, 'sub_menu', None), None)

    def test_sub_menu_items_added_inline_if_option_value_set_to_true(self):
        menu = self.get_render_ready_menu_instance(add_sub_menus_inline=True)
        items_with_children = tuple(
            item for item in menu.get_menu_items_for_rendering()
            if getattr(item, 'has_children_in_menu', False)
        )
        for menu_item in items_with_children:
            self.assertTrue(menu_item.sub_menu)
            self.assertIsInstance(menu_item.sub_menu, menu.get_sub_menu_class())
