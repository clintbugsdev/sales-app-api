from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the users object
    """
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
        min_length=6,
        validators=[validate_password]
    )
    name = serializers.CharField(
        required=True
    )

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')

    def create(self, validated_data):
        """
        Create a new user with encrypted password and return it
        """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """
        Update a user's detail
        """
        instance.email = validated_data['email']
        instance.name = validated_data['name']

        instance.save()

        return instance


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


class ChangePasswordSerializer(serializers.ModelSerializer):
    """
    Serializer for the change password
    """
    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False,
        required=True,
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        required=True,
        min_length=6,
        validators=[validate_password]
    )

    class Meta:
        model = get_user_model()
        fields = ('old_password', 'password')

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user

        if user.pk != instance.pk:
            raise serializers.ValidationError({"authorize": "You don't have permission for this user."})

        instance.set_password(validated_data['new_password'])
        instance.save()

        return instance
