from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

from core import permissions


class PermissionTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.manager = get_user_model().objects.create_user(
            email='manager@testdev.com',
            password='passwordmanager123',
            is_manager=True
        )
        self.staff = get_user_model().objects.create_user(
            email='staff@testdev.com',
            password='passwordstaff123',
        )

    def test_authenticated_manager_returns_true(self):
        """
        Test authenticated user as manager returns true
        """

        request = self.factory.get('/test/')
        request.user = self.manager

        permission_check = permissions.IsAuthenticatedManager()
        permission = permission_check.has_permission(request, None)

        self.assertTrue(permission)

    def test_authenticated_non_manager_returns_false(self):
        """
        Test authenticated user as staff returns false
        """
        request = self.factory.get('/test/')
        request.user = self.staff

        permission_check = permissions.IsAuthenticatedManager()
        permission = permission_check.has_permission(request, None)

        self.assertFalse(permission)
