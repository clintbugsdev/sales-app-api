from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Customer

from customer.serializers import CustomerSerializer

SUPPLIERS_URL = reverse('customer:customer-list')


def detail_url(customer_id):
    """
    Return customer detail URL
    """
    return reverse('customer:customer-detail', args=[customer_id])


class PublicUnitApiTests(TestCase):
    """
    Test the publicity available units API
    """

    def setUp(self):
        self.client = APIClient()

    def test_failed_login_required(self):
        """
        Test that login is required fo retrieving categories
        """
        res = self.client.get(SUPPLIERS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUnitApiTests(TestCase):
    """
    Test the Customer API for authenticated user
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

    def test_successful_retrieve_units_by_manager(self):
        """
        Test success retrieve units by manager
        """
        Customer.objects.create(
            code='132',
            name='The first customer',
            contact_no='32152',
            address='New street',
            email='newcust@testdev.com'
        )
        Customer.objects.create(
            code='134',
            name='The second customer',
            contact_no='32152',
            address='Old street',
            email='oldcust@testdev.com'
        )

        res = self.client.get(SUPPLIERS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        customers = Customer.objects.all().order_by('name')
        serializer = CustomerSerializer(customers, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_successful_retrieve_customers_by_non_manager(self):
        """
        Test success retrieve customers by non-manager
        """
        Customer.objects.create(
            code='135',
            name='The third customer',
            contact_no='32152',
            address='New street',
            email='newcust01@testdev.com'
        )
        Customer.objects.create(
            code='136',
            name='The fourth customer',
            contact_no='32152',
            address='Old street',
            email='oldcust02@testdev.com'
        )

        self.client = APIClient()
        self.client.force_authenticate(self.cashier)
        res = self.client.get(SUPPLIERS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        customers = Customer.objects.all().order_by('name')
        serializer = CustomerSerializer(customers, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_successful_create_customer_by_manager(self):
        """
        Test successful creation of a new customer by manager
        """
        payload = {
            'code': '327',
            'name': 'The fifth customer',
            'contact_no': '1295',
            'address': 'New street',
            'email': 'newcust03@testdev.com'
        }
        res = self.client.post(SUPPLIERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = Customer.objects.filter(
            code=payload['code'],
            name=payload['name'],
        ).exists()

        self.assertTrue(exists)

    def test_failed_create_customer_by_non_manager(self):
        """
        Test failed creation of a new customer by non-manager
        """
        self.client = APIClient()
        self.client.force_authenticate(self.cashier)

        payload = {
            'code': '328',
            'name': 'The sixth customer',
            'contact_no': '532',
            'address': 'Old street again',
            'email': 'oldcust03@testdev.com'
        }
        res = self.client.post(SUPPLIERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        exists = Customer.objects.filter(
            code=payload['code'],
            name=payload['name'],
        ).exists()

        self.assertFalse(exists)

    def test_successful_update_customer_by_manager(self):
        """
        Test successful update customer by manager
        """
        customer = Customer.objects.create(
            code='2137',
            name='The seventh customer',
            contact_no='32152',
            address='New old street',
            email='newcust04@testdev.com'
        )

        payload = {'name': 'The seventh customer name', 'contact_no': '5334'}
        url = detail_url(customer.id)
        self.client.patch(url, payload)

        customer.refresh_from_db()

        self.assertEqual(customer.name, payload['name'])
        self.assertEqual(customer.contact_no, payload['contact_no'])

    def test_failed_create_customer_missing_field(self):
        """
        Test failed creating a new customer with invalid payload
        """
        payload = {
            'code': '',
            'name': 'The eighth customer',
            'contact_no': '532',
            'address': 'New old street again',
            'email': ''
        }
        res = self.client.post(SUPPLIERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
