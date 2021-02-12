from rest_framework import serializers

from core.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer objects"""

    class Meta:
        model = Customer
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
