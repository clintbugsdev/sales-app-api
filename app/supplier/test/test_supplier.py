from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Supplier

from supplier.serializers import SupplierSerializer

SUPPLIERS_URL = reverse('supplier:supplier-list')


def detail_url(supplier_id):
    """
    Return supplier detail URL
    """
    return reverse('supplier:supplier-detail', args=[supplier_id])


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
    Test the Supplier API for authenticated user
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
        Supplier.objects.create(
            code='132',
            name='The first supplier',
            contact_no='32152',
            address='New street',
            email='newsupp@testdev.com'
        )
        Supplier.objects.create(
            code='134',
            name='The second supplier',
            contact_no='32152',
            address='Old street',
            email='oldsupp@testdev.com'
        )

        res = self.client.get(SUPPLIERS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        suppliers = Supplier.objects.all().order_by('name')
        serializer = SupplierSerializer(suppliers, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_successful_retrieve_suppliers_by_non_manager(self):
        """
        Test success retrieve suppliers by non-manager
        """
        Supplier.objects.create(
            code='135',
            name='The third supplier',
            contact_no='32152',
            address='New street',
            email='newsupp01@testdev.com'
        )
        Supplier.objects.create(
            code='136',
            name='The fourth supplier',
            contact_no='32152',
            address='Old street',
            email='oldsupp02@testdev.com'
        )

        self.client = APIClient()
        self.client.force_authenticate(self.cashier)
        res = self.client.get(SUPPLIERS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        suppliers = Supplier.objects.all().order_by('name')
        serializer = SupplierSerializer(suppliers, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_successful_create_supplier_by_manager(self):
        """
        Test successful creation of a new supplier by manager
        """
        payload = {
            'code': '327',
            'name': 'The fifth supplier',
            'contact_no': '1295',
            'address': 'New street',
            'email': 'newsupp03@testdev.com'
        }
        res = self.client.post(SUPPLIERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = Supplier.objects.filter(
            code=payload['code'],
            name=payload['name'],
        ).exists()

        self.assertTrue(exists)

    def test_failed_create_supplier_by_non_manager(self):
        """
        Test failed creation of a new supplier by non-manager
        """
        self.client = APIClient()
        self.client.force_authenticate(self.cashier)

        payload = {
            'code': '328',
            'name': 'The sixth supplier',
            'contact_no': '532',
            'address': 'Old street again',
            'email': 'oldsupp03@testdev.com'
        }
        res = self.client.post(SUPPLIERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        exists = Supplier.objects.filter(
            code=payload['code'],
            name=payload['name'],
        ).exists()

        self.assertFalse(exists)

    def test_successful_update_supplier_by_manager(self):
        """
        Test successful update supplier by manager
        """
        supplier = Supplier.objects.create(
            code='2137',
            name='The seventh supplier',
            contact_no='32152',
            address='New old street',
            email='newsupp04@testdev.com'
        )

        payload = {'name': 'The seventh supplier name', 'contact_no': '5334'}
        url = detail_url(supplier.id)
        self.client.patch(url, payload)

        supplier.refresh_from_db()

        self.assertEqual(supplier.name, payload['name'])
        self.assertEqual(supplier.contact_no, payload['contact_no'])

    def test_failed_create_supplier_missing_field(self):
        """
        Test failed creating a new supplier with invalid payload
        """
        payload = {
            'code': '',
            'name': 'The eighth supplier',
            'contact_no': '532',
            'address': 'New old street again',
            'email': ''
        }
        res = self.client.post(SUPPLIERS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
