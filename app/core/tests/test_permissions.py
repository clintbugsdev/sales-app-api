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

    def test_successful_authenticated_manager(self):
        """
        Test successful authenticated manager
        """

        request = self.factory.get('/test/')
        request.user = self.manager

        permission_check = permissions.IsAuthenticatedManager()
        permission = permission_check.has_permission(request, None)

        self.assertTrue(permission)

    def test_failed_authenticated_non_manager(self):
        """
        Test failed authenticated non manager or as staff
        """
        request = self.factory.get('/test/')
        request.user = self.staff

        permission_check = permissions.IsAuthenticatedManager()
        permission = permission_check.has_permission(request, None)

        self.assertFalse(permission)
