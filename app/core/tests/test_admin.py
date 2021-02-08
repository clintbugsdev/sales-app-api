from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from core import models


def sample_unit(name='gallon', short_name='gal'):
    """
    Create a sample unit for product
    """
    return models.Unit.objects.create(name=name, short_name=short_name)


def sample_category(name='Hardware'):
    """
    Create a sample category for product
    """
    return models.Category.objects.create(name=name)


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@testdev.com',
            password='passwordadmin123'
        )
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email='test@testdev.com',
            password='password123',
            name='Test user full name'
        )

        self.unit = sample_unit()
        self.category = sample_category()

        self.product = models.Product.objects.create(
            code='543',
            name='Test new product',
            unit_id=self.unit.id,
            unit_in_stock=200,
            unit_price=300,
            discount_percentage=10,
            reorder_level=50,
            on_sale=False
        )

        self.supplier = models.Supplier.objects.create(
            code='453453',
            name='Test new supplier',
            contact_no='412384',
            address='2nd Street, Bag City',
            email='supplier@testdev.com'
        )

        self.customer = models.Customer.objects.create(
            code='423423',
            name='Test new customer',
            contact_no='54345345',
            address='2nd Street, Bag City',
            email='customer@testdev.com'
        )

    def test_users_listed(self):
        """
        Test that users are listed on admin page
        """
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """
        Test that the user edit page works
        """
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """
        Test that the create user page works
        """
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_units_listed(self):
        """
        Test that units are listed on admin page
        """

        url = reverse('admin:core_unit_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.unit.name)
        self.assertContains(res, self.unit.short_name)

    def test_unit_change_page(self):
        """
        Test that the unit edit page works
        """
        url = reverse('admin:core_unit_change', args=[self.unit.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_unit_page(self):
        """
        Test that the create unit page works
        """
        url = reverse('admin:core_unit_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_categories_listed(self):
        """
        Test that categories are listed on admin page
        """

        url = reverse('admin:core_category_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.category.name)

    def test_category_change_page(self):
        """
        Test that the category edit page works
        """
        url = reverse('admin:core_category_change', args=[self.category.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_category_page(self):
        """
        Test that the create category page works
        """
        url = reverse('admin:core_category_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_products_listed(self):
        """
        Test that products are listed on admin page
        """

        url = reverse('admin:core_product_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.product.name)

    def test_product_change_page(self):
        """
        Test that the product edit page works
        """
        url = reverse('admin:core_product_change', args=[self.product.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_product_page(self):
        """
        Test that the create product page works
        """
        url = reverse('admin:core_category_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_suppliers_listed(self):
        """
        Test that suppliers are listed on admin page
        """

        url = reverse('admin:core_supplier_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.supplier.name)

    def test_supplier_change_page(self):
        """
        Test that the supplier edit page works
        """
        url = reverse('admin:core_supplier_change', args=[self.supplier.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_supplier_page(self):
        """
        Test that the create supplier page works
        """
        url = reverse('admin:core_supplier_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_customer_listed(self):
        """
        Test that customers are listed on admin page
        """

        url = reverse('admin:core_customer_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.customer.name)

    def test_customer_change_page(self):
        """
        Test that the customer edit page works
        """
        url = reverse('admin:core_customer_change', args=[self.customer.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_customer_page(self):
        """
        Test that the create customer page works
        """
        url = reverse('admin:core_customer_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
