from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the users object
    """
    name = serializers.CharField(required=True)
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=get_user_model().objects.all()
            )
        ]
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        required=True,
        validators=[validate_password]
    )
    is_active = serializers.BooleanField(required=False)
    is_staff = serializers.BooleanField(required=False)

    class Meta:
        model = get_user_model()
        fields = ('id', 'name', 'email', 'password', 'is_active', 'is_staff')
        read_only_fields = ('id',)

    def create(self, validated_data):
        """
        Create a new staff user with encrypted password and return it
        """
        validated_data['is_staff'] = True
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """
        Update a user's detail
        """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """
    Serializer for the user authentication object
    """
    email = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        required=True
    )

    def validate(self, attrs):
        """
        Validate and authenticate the user
        """
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for the change password
    """
    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False,
        required=True,
    )
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False,
        required=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False,
        required=True,
        validators=[validate_password]
    )

    class Meta:
        model = get_user_model()
        fields = ('old_password', 'new_password', 'confirm_password')

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New password and confirm password fields didn't match.")

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct")
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.pk != instance.pk:
            raise serializers.ValidationError("You don't have permission for this user.")

        instance.set_password(validated_data['new_password'])
        instance.save()

        return instance
