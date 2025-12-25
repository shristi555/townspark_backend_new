from rest_framework.permissions import BasePermission


class IsOwnerOrStaff(BasePermission):
    """
    Allow access only to owner or staff users.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True

        # object owner check
        if hasattr(obj, "reported_by"):
            return obj.reported_by == request.user

        if hasattr(obj, "commented_by"):
            return obj.commented_by == request.user

        return False
