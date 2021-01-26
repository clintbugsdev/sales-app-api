from rest_framework.response import Response
from rest_framework import (generics, viewsets, mixins,
                            authentication, permissions, status)
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from core.permissions import IsAuthenticatedManager
from user import serializers


class LoginUserView(ObtainAuthToken):
    """
    Login user by creating own auth token
    """
    serializer_class = serializers.AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class LogoutUserView(APIView):
    """
    Logout user by deleting own auth token
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, format=None):
        """
        Delete auth token to logout user
        """
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileView(generics.RetrieveAPIView):
    """
    Retrieve profile details of an authenticated user
    """
    serializer_class = serializers.UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)


class ChangePasswordView(generics.UpdateAPIView):
    """
    Change password of an authenticated user
    """
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)


class ManageUserViewset(viewsets.GenericAPIView,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin):
    """
    List, create, retrieve, and update user by authenticated manager
    """
    serializer_class = serializers.UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsAuthenticatedManager,)
