from rest_framework import (viewsets, mixins)
from rest_framework.authentication import TokenAuthentication

from core.permissions import IsAuthenticatedManager
from core.models import Category, Unit

from product import serializers


class BaseProductAttrViewSet(viewsets.GenericViewSet,
                             mixins.ListModelMixin,
                             mixins.CreateModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin):
    """
    Base viewset for user owned recipe attributes
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
        return self.queryset.order_by('-name').distinct()

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


class CategoryViewSet(BaseProductAttrViewSet):
    """
    Manage category in the database
    """
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class UnitViewSet(BaseProductAttrViewSet):
    """
    Manage unit in the database
    """
    queryset = Unit.objects.all()
    serializer_class = serializers.UnitSerializer
