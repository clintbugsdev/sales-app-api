from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

LOGIN_URL = reverse('user:login')
LOGOUT_URL = reverse('user:logout')
PROFILE_URL = reverse('user:profile')
USERS_URL = reverse('user:user-list')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
    Test the users API endpoint (public)
    """

    def setUp(self):
        self.client = APIClient()

    def test_successful_user_login(self):
        """
        Test successful user login with valid credentials
        """
        payload = {
            'email': 'test@testdev.com',
            'password': 'testpass'
        }
        create_user(**payload)
        res = self.client.post(LOGIN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_failed_user_login(self):
        """
        Test failed user login with invalid username or email
        """
        payload = {
            'email': 'nouser@testdev.com',
            'password': 'testpass'
        }
        res = self.client.post(LOGIN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failed_user_login_wrong_password(self):
        """
        Test failed user login with wrong password
        """
        payload = {
            'email': 'test@testdev.com',
            'password': 'wrongpass'
        }
        res = self.client.post(LOGIN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failed_user_login_missing_field(self):
        """
        Test failed user login with missing data for email field
        """
        res = self.client.post(LOGIN_URL, {'email': '', 'password': 'testpass'})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateUserApiTests(TestCase):
    """
    Test API requests that require authentication
    """

    def setUp(self):
        self.user = create_user(
            email='test@recipeappdev.com',
            password='password',
            name='name',
            is_manager=True
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_successful_create_user(self):
        """
        Test successful creation of a user with valid payload
        """
        payload = {
            'email': 'test@recipeapp.com',
            'password': 'secret',
            'name': 'Test name',
            'is_staff': True
        }
        res = self.client.post(USERS_URL, payload)
        user = get_user_model().objects.get(**res.data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_failed_create_user_exists(self):
        """
        Test failed create user with existing data
        """
        payload = {
            'email': 'test@recipeapp.com',
            'password': 'testdev'
        }
        create_user(**payload)
        res = self.client.post(USERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failed_create_user_short_password(self):
        """
        Test failed create user with lesser characters than the required
        """
        payload = {
            'name': 'Test',
            'email': 'test@recipeapp.com',
            'password': 'pw'
        }
        res = self.client.post(USERS_URL, payload)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exists)

    def test_successful_retrieve_profile(self):
        """
        Test successful retrieving profile for logged in user
        """
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_failed_post_me_not_allowed(self):
        """
        Test that POST is not allowed on the me url
        """
        res = self.client.post(USERS_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_successful_update_user_profile(self):
        """
        Test successful updating of user profile by the authenticated manager
        """
        payload = {
            'name': 'new name',
            'password': 'newpassword123'
        }

        res = self.client.patch(USERS_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
