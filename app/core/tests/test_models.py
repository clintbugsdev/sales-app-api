import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@testdev.com', password='testpass'):
    """Create a sample user"""

    return get_user_model().objects.create_user(email, password)


def sample_unit(name='gallon', short_name='gal'):
    """Create a sample unit for product"""

    return models.Unit.objects.create(name=name, short_name=short_name)


def sample_category(name='Hardware'):
    """Create a sample category for product"""

    return models.Category.objects.create(name=name)


def sample_product(
        code='01010',
        name='Test prod name',
        unit_in_stock=10,
        unit_price=100.00,
        discount_percentage=1.00,
        reorder_level=10,
        on_sale=True
):
    """Create a sample category for product"""

    return models.Product.objects.create(
        code=code,
        name=name,
        unit=sample_unit(),
        unit_in_stock=unit_in_stock,
        unit_price=unit_price,
        discount_percentage=discount_percentage,
        reorder_level=reorder_level,
        on_sale=on_sale
    )


def sample_supplier(
        code='01010',
        name='Test prod name',
        contact_no=1045345,
        address='2nd Street',
        email='testsupplier312@tesdev.com',
        is_active=True
):
    """Create a sample category for product"""

    return models.Supplier.objects.create(
        code=code,
        name=name,
        contact_no=contact_no,
        address=address,
        email=email,
        is_active=True
    )


class ModelTests(TestCase):

    def test_successful_create_user_valid_email(self):
        """Test successful create user with valid email"""

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
        """Test failed create user with normalized email"""

        email = 'testuser@TESTDEV.COM'
        user = get_user_model().objects.create_user(email, 'testuser123')

        self.assertEqual(user.email, email.lower())

    def test_failed_create_user_invalid_email(self):
        """Test failed create user with no email"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_successful_create_cashier(self):
        """Test successful create cashier with valid credentials"""

        user = get_user_model().objects.create_cashier(
            'testcashier@testdev.com',
            '123test123'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_cashier)
        self.assertFalse(user.is_manager)

    def test_successful_create_manager(self):
        """Test successful create manager with valid credentials"""

        user = get_user_model().objects.create_manager(
            'testmanager@testdev.com',
            '123test123'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_cashier)
        self.assertTrue(user.is_manager)

    def test_successful_create_superuser(self):
        """Test creating a new superuser with valid credentials"""

        user = get_user_model().objects.create_superuser(
            'testsuperuser@recipe.com',
            '123test123'
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_cashier)
        self.assertTrue(user.is_manager)
        self.assertTrue(user.is_superuser)

    def test_successful_category_str(self):
        """Test the category string representation"""

        category = models.Category.objects.create(
            name='Accessories'
        )

        self.assertEqual(str(category), category.name)

    def test_successful_unit_str(self):
        """Test the unit string representation"""

        unit = models.Unit.objects.create(
            name='Piece',
            short_name='pc'
        )

        self.assertEqual(str(unit), unit.name)

    def test_successful_product_str(self):
        """Test the product string representation"""

        product = models.Product.objects.create(
            code='00001',
            name='Oishi Crackers',
            unit=sample_unit(),
            unit_in_stock=100,
            unit_price=10.00,
            discount_percentage=0.00,
            reorder_level=20,
            on_sale=False
        )

        self.assertEqual(str(product), product.name)

    def test_successful_supplier_str(self):
        """Test the supplier string representation"""

        supplier = models.Supplier.objects.create(
            code='00001',
            name='Product supplier 01',
            contact_no='3123123',
            address='1st Street, New Africa',
            email='supp@testdev.com'
        )

        self.assertEqual(str(supplier), supplier.name)

    def test_successful_customer_str(self):
        """Test the customer string representation"""

        customer = models.Customer.objects.create(
            code='4326',
            name='Store customer',
            contact_no='3123125763',
            address='1st Street, New Asia'
        )

        self.assertEqual(str(customer), customer.name)

    def test_successful_purchase_order(self):
        """Test the po number string representation"""

        purchase_order = models.PurchaseOrder.objects.create(
            product=sample_product(),
            quantity=20,
            unit_price=200,
            sub_total=4000,
            required_date=datetime.datetime(2021, 5, 17),
            is_cancelled=False,
            supplier=sample_supplier()
        )
        po_no = f'PO#{purchase_order.id}'
        self.assertEqual(str(purchase_order), po_no)
