from django.test import TestCase

from wagtailmenus.models import ChildrenMenu
from wagtailmenus.tests import utils

Page = utils.get_page_model()


class TestChildrenMenuClass(TestCase):

    def test_init_raises_typeerror_if_max_levels_not_supplied(self):
        msg_extract = "'max_levels' must be provided when creating"
        with self.assertRaisesRegex(TypeError, msg_extract):
            ChildrenMenu(Page(), use_specific=1)

    def test_init_raises_typeerror_if_use_specific_not_supplied(self):
        msg_extract = "'use_specific' must be provided when creating"
        with self.assertRaisesRegex(TypeError, msg_extract):
            ChildrenMenu(Page(), max_levels=1)
