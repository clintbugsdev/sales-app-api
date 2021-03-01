from rest_framework import serializers

from core.models import Product, Supplier, PurchaseOrder


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier objects"""

    class Meta:
        model = Supplier
        fields = (
            'id',
            'code',
            'name',
            'contact_no',
            'address',
            'email',
            'is_active'
        )
        read_only_fields = ('id',)


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for Purchase Order object"""

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
    )

    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
    )

    class Meta:
        model = PurchaseOrder
        fields = (
            'id',
            'product',
            'quantity',
            'unit_price',
            'sub_total',
            'required_date',
            'supplier',
            'is_cancelled'
        )
        read_only_fields = ('id',)
