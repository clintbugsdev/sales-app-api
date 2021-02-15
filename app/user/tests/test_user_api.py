from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from user.serializers import StaffUserSerializer

LOGIN_URL = reverse('user:login')
LOGOUT_URL = reverse('user:logout')
PROFILE_URL = reverse('user:profile')
CHANGE_PASSWORD_URL = reverse('user:change_password')
USERS_URL = reverse('user:user-list')


def create_user(**params):
    """Create new user"""

    return get_user_model().objects.create_user(**params)


def user_url(user_id):
    """Return user detail URL"""

    return reverse('user:user-detail', args=[user_id])


class PublicUserApiTests(TestCase):
    """Test the users API endpoint (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_successful_user_login(self):
        """Test successful user login with valid credentials"""

        payload = {
            'email': 'test@testdev.com',
            'password': 'testpass123'
        }
        create_user(**payload)
        res = self.client.post(LOGIN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_failed_user_login(self):
        """Test failed user login with invalid username or email"""

        payload = {
            'email': 'nouser@testdev.com',
            'password': 'testpass123'
        }
        res = self.client.post(LOGIN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failed_user_login_wrong_password(self):
        """Test failed user login with wrong password"""

        payload = {
            'email': 'test@testdev.com',
            'password': 'wrongpass123'
        }
        res = self.client.post(LOGIN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failed_user_login_missing_field(self):
        """Test failed user login with missing data for email field"""

        res = self.client.post(LOGIN_URL, {
            'email': '',
            'password': 'testpass'
        })

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateManageUserApiTests(TestCase):
    """Test API requests that require authentication from manager"""

    def setUp(self):
        self.manager = create_user(
            email='testmanager@testdev.com',
            password='123password123',
            name='name',
            is_active=True,
            is_staff=True,
            is_cashier=True,
            is_manager=True,
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.manager)

        self.cashier = create_user(
            email='testuser@testdev.com',
            password='321secret321',
            name='name',
            is_active=True,
            is_staff=True,
            is_cashier=True,
            is_manager=False
        )

    def test_successful_retrieve_users_by_manager(self):
        """Test successful retrieve user by manager"""

        get_user_model().objects.create(
            email='testuser001@testdev.com',
            password='321secret321',
            name='name',
            is_active=True,
            is_staff=True,
            is_cashier=True,
            is_manager=False
        )
        get_user_model().objects.create(
            email='testuser002@testdev.com',
            password='321secret321',
            name='name',
            is_active=True,
            is_staff=True,
            is_cashier=False,
            is_manager=False
        )

        res = self.client.get(USERS_URL)

        users = get_user_model() \
            .objects.all().order_by('-id') \
            .filter(is_manager=False).exclude(id=self.manager.id)
        serializer = StaffUserSerializer(users, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_failed_retrieve_users_by_cashier(self):
        """Test failed retrieve users by cashier"""

        self.client = APIClient()
        self.client.force_authenticate(user=self.cashier)
        res = self.client.get(USERS_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_successful_create_user_by_manager(self):
        """Test successful creation of a user with valid payload"""

        payload = {
            'name': 'Test name',
            'email': 'test@testdev.com',
            'password': '321secret321',
            'is_staff': True
        }
        res = self.client.post(USERS_URL, payload)
        user = get_user_model().objects.get(**res.data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_failed_create_user_missing_field(self):
        """Test failed creation of a user with invalid payload"""

        payload = {
            'name': '',
            'email': 'thetestnewuser@testdev.com',
            'password': ''
        }
        res = self.client.post(USERS_URL, payload)
        exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(exists)

    def test_failed_create_user_by_cashier(self):
        """Test failed creation of user by a non-manager user"""

        self.client = APIClient()
        self.client.force_authenticate(user=self.cashier)
        payload = {
            'name': 'Test user',
            'email': 'testforbiddenuser@testdev.com',
            'password': 'testpass123'
        }
        res = self.client.post(USERS_URL, payload)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(user_exists)

    def test_failed_create_user_exists(self):
        """Test failed creation of a user with existing data"""

        payload = {
            'name': 'Test cashier',
            'email': 'testcashier@testdev.com',
            'password': 'testpass312'
        }
        create_user(**payload)
        res = self.client.post(USERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_failed_create_user_short_password(self):
        """Test failed create user w/ short password than the required"""

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

    def test_retrieve_manager_profile_success(self):
        """Test retrieving profile details of an authenticated manager"""

        res = self.client.get(PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'id': self.manager.id,
            'name': self.manager.name,
            'email': self.manager.email,
            'is_active': self.manager.is_active,
            'is_staff': self.manager.is_staff,
            'is_cashier': self.manager.is_cashier,
            'is_manager': self.manager.is_manager
        })

    def test_failed_post_profile_not_allowed(self):
        """Test that POST is not allowed on the profile url"""

        res = self.client.post(PROFILE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_failed_full_update_profile_not_allowed(self):
        """Test that PUT is not allowed on the profile url"""

        res = self.client.put(PROFILE_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_successful_change_own_password(self):
        """Test successful updating of own password"""

        payload = {
            'old_password': '123password123',
            'new_password': '123321password',
            'confirm_password': '123321password',
        }

        res = self.client.patch(CHANGE_PASSWORD_URL, payload)

        self.manager.refresh_from_db()
        self.assertTrue(self.manager.check_password(payload['new_password']))
        self.assertNotIn('123321password', res.data)

    def test_success_partial_update_user_by_manager(self):
        """Test successful partial updating of a manageable user's profile"""

        user = create_user(
            name='Old test name',
            email='testolduser@testdev.com',
            password='secret',
            is_staff=True
        )
        url = user_url(user.id)
        payload = {
            'name': 'New test name',
        }
        res = self.client.patch(url, payload)
        user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(user.name, payload['name'])

    def test_success_full_update_by_manager(self):
        """Test successful updating of a manageable user's profile"""

        user = create_user(
            name='Old new test name',
            email='testnewolduser@testdev.com',
            password='secret',
            is_staff=True)
        url = user_url(user.id)
        payload = {
            'name': 'New test name',
            'email': 'testnew@testdev.com',
            'password': 'secret125434',
            'is_active': True
        }
        res = self.client.put(url, payload)
        user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(user.name, payload['name'])
        self.assertEqual(user.email, payload['email'])
