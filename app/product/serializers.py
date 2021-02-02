from rest_framework import serializers

from core.models import Category, Unit


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for category objects
    """

    class Meta:
        model = Category
        fields = ('id', 'name', 'is_active')
        read_only_field = ('id',)


class UnitSerializer(serializers.ModelSerializer):
    """
    Serializer for unit objects
    """

    class Meta:
        model = Unit
        fields = ('id', 'name', 'short_name', 'is_active')
        read_only_field = ('id',)
