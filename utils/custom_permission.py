from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow only the owner of an object or an admin user
    to read or modify it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.owner == request.user or request.user.is_staff
        return obj.owner == request.user or request.user.is_staff

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
class AllowAnyExceptGuest(permissions.BasePermission):
    """
    Allows unrestricted access unless the user is the guest user.
    Blocks access only for the guest user, even if authenticated.
    """
    GUEST_EMAIL = "guest@exampless.com"

    def has_permission(self, request, view):
        user = request.user
        if user and user.is_authenticated and user.email == self.GUEST_EMAIL:
            return False
        return True