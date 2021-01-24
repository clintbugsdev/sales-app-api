import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@testdev.com', password='testpass'):
    """
    Create  a sample user
    """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """
        Test creating a new user with an email is successful
        """
        email = 'test@testdev.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """
        Test the email for a new user is normalized
        """
        email = 'testuser@TESTDEV.COM'
        user = get_user_model().objects.create_user(email, 'testuser123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """
        Test creating user with no email raises error
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_manager(self):
        """
        Test creating a new manager
        """
        user = get_user_model().objects.create_user(
            email='manager@testdev.com',
            password='test123',
            is_staff=True,
            is_manager=True
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_manager)
        self.assertFalse(user.is_superuser)

    def test_create_new_superuser(self):
        """
        Test creating a new superuser
        """
        user = get_user_model().objects.create_superuser(
            'supertest@recipe.com',
            'test123'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    # def test_category_str(self):
    #     """
    #     Test the category string representation
    #     """
    #     category = models.Category.objects.create(
    #         name='Accessories'
    #     )
    #
    #     self.assertEqual(str(category), category.name)
    #
    # def test_unit_str(self):
    #     """
    #     Test the unit string representation
    #     """
    #     unit = models.Unit.objects.create(
    #         name='Piece',
    #         short_name='pc'
    #     )
    #
    #     self.assertEqual(str(unit), unit.name)
    #
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
