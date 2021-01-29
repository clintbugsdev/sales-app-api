from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

LOGIN_URL = reverse('user:login')
LOGOUT_URL = reverse('user:logout')
PROFILE_URL = reverse('user:profile')
CHANGE_PASSWORD_URL = reverse('user:change-password')
USERS_URL = reverse('user:user-list')


def create_user(**params):
    """
    Create new user
    """
    return get_user_model().objects.create_user(**params)


def user_url(user_id):
    """
    Return user detail URL
    """
    return reverse('user:user-detail', args=[user_id])


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


class PrivateManageUserApiTests(TestCase):
    """
    Test API requests that require authentication from manager
    """

    def setUp(self):
        self.manager = create_user(
            email='testmanager@testdev.com',
            password='password',
            name='name',
            is_manager=True
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.manager)

        self.staff = create_user(
            email='testuser@testdev.com',
            password='password',
            name='name',
            is_staff=True
        )

    def test_successful_create_user_by_manager(self):
        """
        Test successful creation of a user with valid payload
        """
        payload = {
            'name': 'Test name',
            'email': 'test@testdev.com',
            'password': 'secret',
            'is_staff': True
        }
        res = self.client.post(USERS_URL, payload)
        user = get_user_model().objects.get(**res.data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_failed_create_user_missing_field(self):
        """
        Test failed creation of a user with invalid payload
        """
        payload = {
            'name': '',
            'email': 'testuser@testdev.com',
            'password': ''
        }
        res = self.client.post(USERS_URL, payload)
        exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(exists)

    def test_failed_create_user_by_non_manager(self):
        """
        Test failed creation of user by a non-manager user
        """
        self.client = APIClient()
        self.client.force_authenticate(user=self.staff)
        payload = {
            'name': 'Test user',
            'email': 'testuser@testdev.com',
            'password': 'testpass'
        }
        res = self.client.post(USERS_URL, payload)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(user_exists)

    def test_failed_create_user_exists(self):
        """
        Test failed create user with existing data
        """
        payload = {
            'name': 'Test staff',
            'email': 'teststaff@testdev.com',
            'password': 'testpass'
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
            'email': 'test@testdev.com',
            'password': 'pw'
        }
        res = self.client.post(USERS_URL, payload)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_exists)

    def test_retrieve_profile_success(self):
        """
        Test retrieving profile for logged in user
        """
        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_failed_post_profile_not_allowed(self):
        """
        Test that POST is not allowed on the profile url
        """
        res = self.client.post(PROFILE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_failed_full_update_profile_not_allowed(self):
        """
        Test that PUT is not allowed on the profile url
        """
        res = self.client.put(PROFILE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_successful_partial_update_manager_own_profile(self):
        """
        Test successful updating of manager's own profile details
        """
        payload = {
            'name': 'new name',
        }

        res = self.client.patch(PROFILE_URL, payload)

        self.manager.refresh_from_db()
        self.assertEqual(self.manager.name, payload['name'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_success_partial_update_user_by_manager(self):
        """
        Test success partial updating of other user's profile details
        """
        user = create_user({
            'name': 'Old test name',
            'email': 'testolduser@testdev.com',
            'password': 'secret',
            'is_staff': True
        })
        url = user_url(user.id)
        payload = {
            'name': 'New test name',
        }
        self.client(url, payload)
        res = self.client.patch(USERS_URL, payload)
        user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(user.name, payload['name'])

    def test_failed_full_update_not_allowed_by_manager(self):
        """
        Test success full updating of other user's profile details
        """
        user = create_user({
            'name': 'New Old test name',
            'email': 'testnewolduser@testdev.com',
            'password': 'secret',
            'is_staff': True
        })
        url = user_url(user.id)
        payload = {
            'name': 'New test name',
            'email': 'testnew@testdev.com',
            'password': 'secret',
            'is_staff': True
        }
        self.client(url, payload)
        res = self.client.put(USERS_URL, payload)
        user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertNotEqual(user.name, payload['name'])
