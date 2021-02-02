# import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@testdev.com', password='testpass'):
    """
    Create a sample user
    """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_successful_create_user_valid_email(self):
        """
        Test successful create user with valid email
        """
        email = 'testuser@testdev.com'
        password = 'Testpass123'
        name = 'Tester'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            name=name
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.name, name)

    def test_failed_create_user_normalized_email(self):
        """
        Test failed create user with normalized email
        """
        email = 'testuser@TESTDEV.COM'
        user = get_user_model().objects.create_user(email, 'testuser123')

        self.assertEqual(user.email, email.lower())

    def test_failed_create_user_invalid_email(self):
        """
        Test failed create user with no email
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_successful_create_cashier(self):
        """
        Test successful create cashier with valid credentials
        """
        user = get_user_model().objects.create_cashier(
            'testcashier@testdev.com',
            '123test123'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_cashier)
        self.assertFalse(user.is_manager)

    def test_successful_create_manager(self):
        """
        Test successful create manager with valid credentials
        """
        user = get_user_model().objects.create_manager(
            'testmanager@testdev.com',
            '123test123'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_cashier)
        self.assertTrue(user.is_manager)

    def test_successful_create_superuser(self):
        """
        Test creating a new superuser with valid credentials
        """
        user = get_user_model().objects.create_superuser(
            'testsuperuser@recipe.com',
            '123test123'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_cashier)
        self.assertTrue(user.is_manager)
        self.assertTrue(user.is_superuser)

    def test_category_str(self):
        """
        Test the category string representation
        """
        category = models.Category.objects.create(
            name='Accessories'
        )

        self.assertEqual(str(category), category.name)

    def test_unit_str(self):
        """
        Test the unit string representation
        """
        unit = models.Unit.objects.create(
            name='Piece',
            short_name='pc'
        )

        self.assertEqual(str(unit), unit.name)

    # def test_customer_str(self):
    #     """
    #     Test the customer string representation
    #     """
    #     customer = models.Customer.objects.create(
    #         code='00001',
    #         name='Juan Luna',
    #         birthdate=datetime.date(2001, 1, 1),
    #         gender='Male',
    #         contact='+09232123',
    #         address='1st Road, Baguio City 2601',
    #         email='cust@testdev.com',
    #     )
    #
    #     self.assertEqual(str(customer), customer.name)
