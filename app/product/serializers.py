from rest_framework import serializers

from core.models import Category, Unit, Product


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category objects"""

    class Meta:
        model = Category
        fields = ('id', 'name', 'is_active')
        read_only_field = ('id',)


class UnitSerializer(serializers.ModelSerializer):
    """Serializer for unit objects"""

    class Meta:
        model = Unit
        fields = ('id', 'name', 'short_name', 'is_active')
        read_only_field = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    """Serialize for product objects"""

    unit = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
    )

    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all()
    )

    class Meta:
        model = Product
        fields = (
            'id', 'code', 'name',
            'unit', 'unit_in_stock', 'unit_price',
            'categories',
            'discount_percentage',
            'reorder_level', 'on_sale'
        )
        read_only_fields = ('id',)


class ProductDetailSerializer(ProductSerializer):
    """Serialize a product detail"""

    unit = UnitSerializer(read_only=True)

    categories = CategorySerializer(
        many=True,
        read_only=True
    )
