import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (Unit,
                         Category,
                         Product,
                         Supplier,
                         PurchaseOrder)

from supplier.serializers import PurchaseOrderSerializer

PURCHASE_ORDERS_URL = reverse('supplier:purchase-order-list')


def detail_url(purchase_order_id):
    """Return purchase order detail URL"""

    return reverse('supplier:purchase-order-detail', args=[purchase_order_id])


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


def sample_supplier(**params):
    defaults = {
        'code': '000101',
        'name': 'Jeza',
        'contact_no': 1010,
        'address': 'Central Balili, LTB',
        'email': 'testsupp@testdev.com'
    }
    defaults.update(params)

    return Supplier.objects.create(**defaults)


def sample_purchase_order(product, supplier, **params):
    defaults = {
        'quantity': 120,
        'unit_price': 110,
        'sub_total': 1320,
        'required_date': datetime.datetime(2021, 5, 17),
    }
    defaults.update(params)

    return PurchaseOrder.objects.create(
        product=product,
        supplier=supplier,
        **defaults
    )


class PublicPurchaseOrderApiTests(TestCase):
    """Test the publicity available units API"""

    def setUp(self):
        self.client = APIClient()

    def test_failed_login_required(self):
        """Test that login is required for retrieving purchase order"""

        res = self.client.get(PURCHASE_ORDERS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePurchaseOrderApiTests(TestCase):
    """Test the Purchase Order API for authenticated user"""

    def setUp(self):
        self.client = APIClient()
        self.manager = get_user_model().objects.create_manager(
            'testmanager003@testdev.com',
            'testmanpassword3214'
        )
        self.client.force_authenticate(self.manager)

        self.cashier = get_user_model().objects.create_cashier(
            'testcashier04@testdev.com',
            'passtest0231'
        )
        self.staff = get_user_model().objects.create_user(
            'teststaff05@testdev.com',
            'testpass321123'
        )

    def test_successful_retrieve_orders_by_manager(self):
        """Test successful retrieving a list of po by manager"""

        res = self.client.get(PURCHASE_ORDERS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        purchase_orders = PurchaseOrder.objects.all()
        serializer = PurchaseOrderSerializer(purchase_orders, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_failed_retrieve_orders_by_non_manager(self):
        """Test failed retrieve orders by non-manager"""

        self.client = APIClient()
        self.client.force_authenticate(self.cashier)
        res = self.client.get(PURCHASE_ORDERS_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_successful_create_order_by_manager(self):
        """Test successful creation of a new order by manager"""

        unit = sample_unit()
        product = sample_product(unit=unit, name='Manggo')
        supplier = sample_supplier()

        payload = {
            'product': product.id,
            'quantity': 80,
            'unit_price': 120,
            'sub_total': 9600,
            'required_date': datetime.datetime(2021, 5, 17),
            'supplier': supplier.id,
            'is_cancelled': False
        }
        res = self.client.post(PURCHASE_ORDERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = PurchaseOrder.objects.filter(
            product=payload['product'],
            quantity=payload['quantity'],
            unit_price=payload['unit_price'],
            sub_total=payload['sub_total'],
            supplier=payload['supplier'],
        ).exists()

        self.assertTrue(exists)
