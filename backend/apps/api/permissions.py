from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """Разрешение на чтение для всех и изменение только владельцу."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, 'author', None) or getattr(obj, 'user', None)
        return owner == request.user

    def has_permission(self, request, view):
        return request.user.is_authenticated or request.method in [
            'GET', 'HEAD', 'OPTIONS'
        ]
