from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Unit, Category, Product
from product.serializers import ProductSerializer, ProductDetailSerializer

PRODUCTS_URL = reverse('product:product-list')


def detail_url(product_id):
    """Return product detail URL"""

    return reverse('product:product-detail', args=[product_id])


def sample_unit(name='box', short_name='bx'):
    """Create and return a sample unit"""

    return Unit.objects.create(name=name, short_name=short_name)


def sample_category(name='Bags'):
    """Create and return a sample category"""

    return Category.objects.create(name=name)


def sample_product(unit, **params):
    defaults = {
        'code': '000101',
        'name': 'Ginebra',
        'unit_in_stock': 100,
        'unit_price': 100,
        'discount_percentage': 0,
        'reorder_level': 50
    }
    defaults.update(params)

    return Product.objects.create(unit=unit, **defaults)


class PublicProductApiTests(TestCase):
    """Test unauthenticated product API access"""

    def setUp(self):
        self.client = APIClient()

    def test_failed_login_required(self):
        """
        Test that authentication is required
        """
        res = self.client.get(PRODUCTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProductApiTests(TestCase):
    """Test the Product API for authenticated user"""

    def setUp(self):
        self.client = APIClient()
        self.manager = get_user_model().objects.create_manager(
            'testmanager002@testdev.com',
            'testmanpassword3214'
        )
        self.client.force_authenticate(self.manager)

        self.cashier = get_user_model().objects.create_cashier(
            'testcashier03@testdev.com',
            'passtest0231'
        )
        self.staff = get_user_model().objects.create_user(
            'teststaff02@testdev.com',
            'testpass321123'
        )

    def test_successful_retrieve_products_by_manager(self):
        """Test successful retrieving a list of products by manager"""

        sample_product(unit=sample_unit())
        sample_product(unit=sample_unit(), **{
            'name': 'Novellino',
            'code': '3213'
        })

        res = self.client.get(PRODUCTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        products = Product.objects.all().order_by('name')
        serializer = ProductSerializer(products, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_successful_retrieve_products_by_non_manager(self):
        """Test successful retrieving a list of products by cashier"""

        sample_product(unit=sample_unit())
        sample_product(unit=sample_unit())

        self.client = APIClient()
        self.client.force_authenticate(self.cashier)
        res = self.client.get(PRODUCTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        products = Product.objects.all().order_by('name')
        serializer = ProductSerializer(products, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_success_view_product_detail_by_non_manager(self):
        """Test viewing a product detail"""

        unit = sample_unit()
        product = sample_product(unit=unit)
        product.categories.add(sample_category())

        url = detail_url(product.id)
        self.client = APIClient()
        self.client.force_authenticate(self.cashier)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer = ProductDetailSerializer(product)

        self.assertEqual(res.data, serializer.data)

    def test_successful_create_product_by_manager(self):
        """Test successful creation of a new product by manager"""

        unit = sample_unit()
        payload = {
            'code': '313543',
            'name': 'Test product',
            'unit': unit.id,
            'unit_in_stock': 200,
            'unit_price': 150,
            'discount_percentage': 0,
            'reorder_level': 50,
            'on_sale': False
        }
        res = self.client.post(PRODUCTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = Product.objects.filter(
            code=payload['code']
        ).exists()

        self.assertTrue(exists)
        self.assertFalse(res.data['on_sale'])

    def test_successful_create_product_with_cat_by_manager(self):
        """Test successful creation of a
        new product with categories by manager"""

        unit = sample_unit()
        category1 = sample_category(name='Phones')
        category2 = sample_category(name='Computers')

        payload = {
            'code': '313543',
            'name': 'Test product',
            'unit': unit.id,
            'unit_in_stock': 200,
            'unit_price': 150,
            'categories': [category1.id, category2.id],
            'discount_percentage': 0,
            'reorder_level': 50,
            'on_sale': False
        }
        res = self.client.post(PRODUCTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        product = Product.objects.get(id=res.data['id'])
        categories = product.categories.all()

        self.assertEqual(categories.count(), 2)
        self.assertIn(category1, categories)
        self.assertIn(category2, categories)

    def test_failed_create_product_by_non_manager(self):
        """Test failed creation of a new product by cashier"""

        unit = sample_unit()
        payload = {
            'code': '43212',
            'name': 'Test cashier product',
            'unit': unit.id,
            'unit_in_stock': 100,
            'unit_price': 100,
            'discount_percentage': 0,
            'reorder_level': 20,
            'on_sale': True
        }
        self.client = APIClient()
        self.client.force_authenticate(self.cashier)
        res = self.client.post(PRODUCTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        exists = Product.objects.filter(
            code=payload['code']
        ).exists()

        self.assertFalse(exists)

    def test_successful_full_update_product_by_manager(self):
        """Test successful full update product by manager"""

        unit1 = sample_unit(name='kilogram', short_name='kg')
        unit2 = sample_unit(name='gram', short_name='g')
        product = sample_product(unit=unit1)
        product.categories.add(sample_category(name='Shoes'))

        payload = {
            'code': '543',
            'name': 'Test new product',
            'unit': unit2.id,
            'unit_in_stock': 200,
            'unit_price': 300,
            'discount_percentage': 10,
            'reorder_level': 50,
            'on_sale': False
        }
        url = detail_url(product.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        product.refresh_from_db()
        self.assertEqual(product.code, payload['code'])
        self.assertEqual(product.name, payload['name'])
        self.assertEqual(product.unit.id, payload['unit'])
        self.assertEqual(product.unit_in_stock, payload['unit_in_stock'])
        self.assertEqual(product.unit_price, payload['unit_price'])
        self.assertEqual(
            product.discount_percentage,
            payload['discount_percentage']
        )
        self.assertEqual(product.reorder_level, payload['reorder_level'])
        self.assertEqual(product.on_sale, payload['on_sale'])

        categories = product.categories.all()
        self.assertEqual(len(categories), 0)

    def test_successful_partial_update_product_by_manager(self):
        """Test successful partial update product by manager"""

        unit = sample_unit(name='liter', short_name='l')
        product = sample_product(unit=unit)
        new_category = sample_category(name='Belt')

        payload = {
            'code': '432143',
            'name': 'Test new product',
            'categories': [new_category.id]
        }
        url = detail_url(product.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        product.refresh_from_db()
        self.assertEqual(product.code, payload['code'])
        self.assertEqual(product.name, payload['name'])

        categories = product.categories.all()
        self.assertEqual(len(categories), 1)
        self.assertIn(new_category, categories)

    def test_failed_partial_update_product_by_non_manager(self):
        """Test failed partial update product by cashier"""

        unit = sample_unit(name='liter', short_name='l')
        product = sample_product(unit=unit)
        new_category = sample_category(name='Socks')

        payload = {
            'code': '6544',
            'name': 'Test partial update product',
            'categories': [new_category.id]
        }
        url = detail_url(product.id)

        self.client = APIClient()
        self.client.force_authenticate(self.cashier)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        product.refresh_from_db()
        self.assertNotEqual(product.code, payload['code'])
        self.assertNotEqual(product.name, payload['name'])

        categories = product.categories.all()
        self.assertNotEqual(len(categories), 1)
        self.assertNotIn(new_category, categories)
