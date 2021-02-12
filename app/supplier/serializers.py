from rest_framework import serializers

from core.models import Supplier


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
