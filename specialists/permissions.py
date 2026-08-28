from rest_framework.permissions import BasePermission


class IsAdminOrLinkedSpecialist(BasePermission):
    """
    View-level permission for specialist-scoped URLs (e.g. /specialists/<pk>/appointments/).
    Passes for admin (is_staff) or a user whose specialist_profile matches the URL's pk.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        specialist_profile = getattr(request.user, "specialist_profile", None)
        if specialist_profile is None:
            return False
        return specialist_profile.id == view.kwargs.get("pk")
