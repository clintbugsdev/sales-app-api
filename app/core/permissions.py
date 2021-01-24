from rest_framework import permissions


class IsAuthenticatedManager(permissions.BasePermission):
    """
    Allows access only to managers or superusers
    """

    def has_permission(self, request, view):
        if bool(request.user and request.user.is_authenticated):
            return bool(request.user.is_manager or request.user.is_superuser)
        return False
