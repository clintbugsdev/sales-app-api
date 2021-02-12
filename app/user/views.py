from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import (generics, viewsets, mixins,
                            authentication, permissions, status)
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from core.permissions import IsAuthenticatedManager
from user.serializers import (AuthTokenSerializer, UserSerializer,
                              ChangePasswordSerializer, StaffUserSerializer)


class LoginUserView(ObtainAuthToken):
    """
    Login user by creating own auth token
    """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class LogoutUserView(APIView):
    """
    Logout user by deleting own auth token
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request):
        """
        Delete auth token to logout user
        """
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileView(generics.RetrieveAPIView):
    """
    Retrieve profile details of an authenticated user
    """
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """
        Retrieve and return authenticated user
        """
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """
    Change password of an authenticated user
    """
    serializer_class = ChangePasswordSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """
        Retrieve and return authenticated user
        """
        return self.request.user


class ManageUserViewset(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin):
    """List, create, retrieve, and update user by authenticated manager"""

    serializer_class = UserSerializer
    queryset = get_user_model().objects.all().order_by('-id')
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsAuthenticatedManager,)

    def get_queryset(self):
        """Retrieve the users to manage"""

        params = {'is_superuser': False}
        if self.request.user.is_manager and not self.request.user.is_superuser:
            params['is_manager'] = False

        return self.queryset.filter(**params).exclude(id=self.request.user.id)

    def get_serializer_class(self):
        """Return appropriate serializer class"""

        if not self.request.user.is_superuser:
            return StaffUserSerializer

        return self.serializer_class
