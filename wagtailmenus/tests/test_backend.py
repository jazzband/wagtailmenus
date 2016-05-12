from __future__ import absolute_import, unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TransactionTestCase
from wagtail.wagtailcore.models import Site


class TestSuperUser(TransactionTestCase):
    fixtures = ['test.json']

    def setUp(self):
        user = get_user_model().objects._create_user(
            username='test1', email='test1@email.com', password='password',
            is_staff=True, is_superuser=True)
        self.client.login(username='test1', password='password')

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

        # Test 'get_error_message' method on view for additional coverage
        view = response.context['view']
        self.assertTrue(view.get_error_message())

    def test_mainmenu_edit_multisite(self):
        Site.objects.create(
            hostname='test2.com', port=80, root_page_id=2,
            is_default_site=0, site_name="Test site 2")
        Site.objects.create(
            hostname='test3.com', port=80, root_page_id=3,
            is_default_site=0, site_name="Test site 3")

        response = self.client.get(
            '/admin/modeladmin/wagtailmenus/mainmenu/edit/1/')
        self.assertEqual(response.status_code, 200)

        # If the site id in the URL and the site GET value are the same,
        # we shouldn't be redirect, because we're already where we need to be
        response = self.client.get(
            '/admin/modeladmin/wagtailmenus/mainmenu/edit/2/', {'site': 2})
        self.assertEqual(response.status_code, 200)

        # If the site id in the URL and the site GET value are different,
        # we should be redirected to the edit page for the site in GET
        response = self.client.get(
            '/admin/modeladmin/wagtailmenus/mainmenu/edit/2/', {'site': 3})
        self.assertRedirects(response, '/admin/modeladmin/wagtailmenus/mainmenu/edit/3/')

    def test_flatmenu_list(self):
        response = self.client.get('/admin/modeladmin/wagtailmenus/flatmenu/')
        self.assertEqual(response.status_code, 200)

    def test_flatmenu_edit(self):
        response = self.client.get(
            '/admin/modeladmin/wagtailmenus/flatmenu/edit/1/')
        self.assertEqual(response.status_code, 200)


class TestNonSuperUser(TransactionTestCase):
    fixtures = ['perms.json', 'test.json']

    def setUp(self):
        user = get_user_model().objects._create_user(
            username='test2', email='test2@email.com', password='password',
            is_staff=True, is_superuser=False, is_active=True)
        for group in Group.objects.all():
            if group.name == 'Testers':
                user.groups.add(group)
        # Login
        self.client.login(username='test2', password='password')

    def test_mainmenu_edit_denied(self):
        response = self.client.get('/admin/modeladmin/wagtailmenus/mainmenu/edit/1/')
        self.assertEqual(response.status_code, 403)
