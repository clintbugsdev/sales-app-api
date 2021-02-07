from rest_framework import (viewsets, mixins)
from rest_framework.authentication import TokenAuthentication

from core.permissions import IsAuthenticatedManager
from core.models import Category, Unit, Product

from product import serializers


class BaseProductAttrViewSet(viewsets.GenericViewSet,
                             mixins.ListModelMixin,
                             mixins.CreateModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin):
    """
    Base viewset for user owned product attributes
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes_by_action = {
        'create': [IsAuthenticatedManager],
        'update': [IsAuthenticatedManager],
        'partial_update': [IsAuthenticatedManager],
    }

    def get_queryset(self):
        """
        Return objects
        """
        return self.queryset.order_by('name').distinct()

    def get_permissions(self):
        """
        Return permission_classes depending on action
        """
        try:
            # return permission_classes depending on `action`
            return [
                permission()
                for permission
                in self.permission_classes_by_action[self.action]
            ]
        except KeyError:
            # action is not set return default permission_classes
            return [
                permission()
                for permission
                in self.permission_classes
            ]


class UnitViewSet(BaseProductAttrViewSet):
    """
    Manage unit in the database
    """
    queryset = Unit.objects.all()
    serializer_class = serializers.UnitSerializer


class CategoryViewSet(BaseProductAttrViewSet):
    """
    Manage category in the database
    """
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class ProductViewSet(BaseProductAttrViewSet):
    """
    Manage product in the database
    """
    queryset = Product.objects.all().order_by('name')
    serializer_class = serializers.ProductSerializer

    permission_classes_by_action = {
        'create': [IsAuthenticatedManager],
        'update': [IsAuthenticatedManager],
        'partial_update': [IsAuthenticatedManager],
    }

    def _params_to_ints(self, qs):
        """
        Convert a list of string IDs to a list of integers
        """
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """
        Retrieve the products for the authenticated user
        """
        unit = self.request.query_params.get('unit')
        categories = self.request.query_params.get('categories')
        queryset = self.queryset

        if unit:
            unit_ids = self._params_to_ints(unit)
            queryset = queryset.filter(unit_id__in=unit_ids)
        if categories:
            category_ids = self._params_to_ints(categories)
            queryset = queryset.filter(categories__id__in=category_ids)

        return queryset.filter()

    def get_serializer_class(self):
        """
        Retrieve appropriate serializer class
        """
        if self.action == 'retrieve':
            return serializers.ProductDetailSerializer

        return self.serializer_class
