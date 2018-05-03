from django.test import TestCase

from wagtailmenus.models import SectionMenu
from wagtailmenus.tests import utils

Page = utils.get_page_model()


class TestSectionMenuClass(TestCase):

    def test_init_raises_typeerror_if_use_specific_not_supplied(self):
        with self.assertRaises(TypeError):
            SectionMenu(Page(), 1)
