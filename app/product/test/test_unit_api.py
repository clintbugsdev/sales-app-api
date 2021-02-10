from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Unit

from product.serializers import UnitSerializer

UNITS_URL = reverse('product:unit-list')


def detail_url(unit_id):
    """
    Return unit detail URL
    """
    return reverse('product:unit-detail', args=[unit_id])


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
        res = self.client.get(UNITS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUnitApiTests(TestCase):
    """
    Test the Unit API for authenticated user
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
        Unit.objects.create(name='kilogram', short_name='kg')
        Unit.objects.create(name='piece', short_name='pc')

        res = self.client.get(UNITS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        units = Unit.objects.all().order_by('name')
        serializer = UnitSerializer(units, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_successful_retrieve_units_by_non_manager(self):
        """
        Test success retrieve units by non-manager
        """
        Unit.objects.create(name='T-shirts')
        Unit.objects.create(name='Hardware')

        self.client = APIClient()
        self.client.force_authenticate(self.cashier)
        res = self.client.get(UNITS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        units = Unit.objects.all().order_by('name')
        serializer = UnitSerializer(units, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_successful_create_unit_by_manager(self):
        """
        Test successful creation of a new unit by manager
        """
        payload = {'name': 'feet', 'short_name': 'ft'}
        res = self.client.post(UNITS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        exists = Unit.objects.filter(
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_failed_create_unit_by_non_manager(self):
        """
        Test failed creation of a new unit by non-manager
        """
        self.client = APIClient()
        self.client.force_authenticate(self.cashier)

        payload = {'name': 'meter', 'short_name': 'm'}
        res = self.client.post(UNITS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        exists = Unit.objects.filter(
            name=payload['name']
        ).exists()

        self.assertFalse(exists)

    def test_successful_update_unit_by_manager(self):
        """
        Test successful update unit by manager
        """
        unit = Unit.objects.create(name='liter', short_name='lt')

        payload = {'name': 'gram', 'short_name': 'g'}
        url = detail_url(unit.id)
        self.client.patch(url, payload)

        unit.refresh_from_db()

        self.assertEqual(unit.name, payload['name'])
        self.assertEqual(unit.short_name, payload['short_name'])

    def test_failed_create_unit_missing_field(self):
        """
        Test failed creating a new unit with invalid payload
        """
        payload = {'name': '', 'short_name': 'y'}
        res = self.client.post(UNITS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
