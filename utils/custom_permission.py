from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow only the owner of an object or an admin user
    to read or modify it.
    """

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS = GET, HEAD, OPTIONS (read-only access)
        if request.method in permissions.SAFE_METHODS:
            print(f'Checking object permission for user {request.user}, object owner: {getattr(obj, 'owner', None)}')
            
            return obj.owner == request.user or request.user.is_staff

        # For write permissions (POST, PATCH, DELETE), only allow owner or admin
        return obj.owner == request.user or request.user.is_staff

    def has_permission(self, request, view):
        # Allow general access for POST requests only if user is authenticated
        return request.user and request.user.is_authenticated