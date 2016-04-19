from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from wagtail.wagtailcore.models import Site


class TestBackend(TransactionTestCase):
    fixtures = ['test.json']

    @staticmethod
    def get_or_create_test_user():
        """
        Override this method to return an instance of your custom user model
        """
        user_model = get_user_model()
        # Create a user
        user_data = dict()
        user_data['username'] = 'test@email.com'
        user_data['password'] = 'password'

        for field in user_model.REQUIRED_FIELDS:
            user_data[field] = field

        try:
            return user_model.objects.get(username__exact='test@email.com')
        except user_model.DoesNotExist:
            return user_model.objects.create_superuser(**user_data)

    def login(self):
        user_model = get_user_model()
        user = self.get_or_create_test_user()
        self.assertTrue(
            self.client.login(password='password', **{'username': 'test@email.com'})
        )
        return user

    def setUp(self):
        self.login()

    def test_menupage_create(self):
        response = self.client.get('/admin/pages/add/tests/toplevelpage/5/')
        self.assertEqual(response.status_code, 200)

    def test_menupage_edit(self):
        response = self.client.get('/admin/pages/6/edit/')
        self.assertEqual(response.status_code, 200)

    def test_mainmenu_list(self):
        response = self.client.get('/admin/modeladmin/wagtailmenus/mainmenu/')
        self.assertRedirects(response, '/admin/modeladmin/wagtailmenus/mainmenu/edit/1/')

    def test_mainmenu_edit(self):
        response = self.client.get(
            '/admin/modeladmin/wagtailmenus/mainmenu/edit/1/')
        self.assertEqual(response.status_code, 200)

    def test_mainmenu_edit_multisite(self):
        site2 = Site.objects.create(
            hostname='test2.com', port=80, root_page_id=2,
            is_default_site=0, site_name="Test site 2")
        site3 = Site.objects.create(
            hostname='test3.com', port=80, root_page_id=3,
            is_default_site=0, site_name="Test site 3")
        response = self.client.get(
            '/admin/modeladmin/wagtailmenus/mainmenu/edit/1/')
        self.assertEqual(response.status_code, 200)

    def test_flatmenu_list(self):
        response = self.client.get('/admin/modeladmin/wagtailmenus/flatmenu/')
        self.assertEqual(response.status_code, 200)

    def test_flatmenu_edit(self):
        response = self.client.get(
            '/admin/modeladmin/wagtailmenus/flatmenu/edit/1/')
        self.assertEqual(response.status_code, 200)
