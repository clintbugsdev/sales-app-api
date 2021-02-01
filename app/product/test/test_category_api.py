from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Category

from product.serializers import CategorySerializer

CATEGORIES_URL = reverse('product:category-list')


def category_detail_url(category_id):
    """
    Return category detail URL
    """
    return reverse('product:category-detail', args=[category_id])


class PublicCategoryApiTests(TestCase):
    """
    Test the publicity available categories API
    """

    def setUp(self):
        self.client = APIClient()

    def test_failed_login_required(self):
        """
        Test that login is required fo retrieving categories
        """
        res = self.client.get(CATEGORIES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCategoryApiTests(TestCase):
    """
    Test the authorized user category API
    """

    def setUp(self):
        self.manager = get_user_model().objects.create_manager(
            'testmanager01@testdev.com',
            'passtest123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.manager)

        self.cashier = get_user_model().objects.create_cashier(
            'testcashieruser@testdev.com',
            'passtest123'
        )

    def test_successful_retrieve_categories_by_manager(self):
        """
        Test success retrieve categories by manager
        """
        Category.objects.create(name='Toys')
        Category.objects.create(name='Ladies Ware')

        res = self.client.get(CATEGORIES_URL)

        categories = Category.objects.all().order_by('-name')
        serializer = CategorySerializer(categories, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_successful_retrieve_categories_by_non_manager(self):
        """
        Test success retrieve categories by non-manager
        """
        Category.objects.create(name='T-shirts')
        Category.objects.create(name='Hardware')

        self.client = APIClient()
        self.client.force_authenticate(self.cashier)
        res = self.client.get(CATEGORIES_URL)

        categories = Category.objects.all().order_by('-name')
        serializer = CategorySerializer(categories, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_successful_create_category_by_manager(self):
        """
        Test successful creation of a new category by manager
        """
        payload = {'name': 'Test category'}
        res = self.client.post(CATEGORIES_URL, payload)
        exists = Category.objects.filter(
            name=payload['name']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_failed_create_category_by_non_manager(self):
        """
        Test failed creation of a new category by non-manager
        """
        self.client = APIClient()
        self.client.force_authenticate(self.cashier)

        payload = {'name': 'Test failed category'}
        res = self.client.post(CATEGORIES_URL, payload)
        exists = Category.objects.filter(
            name=payload['name']
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(exists)

    def test_successful_update_category_by_manager(self):
        """
        Test successful update category by manager
        """
        category = Category.objects.create(name='Test old category')

        payload = {'name': 'Test new category'}
        url = category_detail_url(category.id)
        self.client.patch(url, payload)

        category.refresh_from_db()
        self.assertEqual(category.name, payload['name'])

    def test_failed_create_category_missing_field(self):
        """
        Test failed creating a new category with invalid payload
        """
        payload = {'name': ''}
        res = self.client.post(CATEGORIES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
