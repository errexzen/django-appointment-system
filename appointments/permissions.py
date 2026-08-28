from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """Object-level: admin (is_staff) or the appointment's customer (owner)."""
    def has_object_permission(self, request, view, obj):
        return request.user and (request.user.is_staff or obj.user_id == request.user.id)


class IsNotSpecialist(BasePermission):
    """Denies access to users who have a linked specialist profile (specialist role)."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return True  # unauthenticated handled by IsAuthenticated, not here
        return getattr(request.user, "specialist_profile", None) is None


class IsAdminOrAssignedSpecialist(BasePermission):
    """
    View-level: must be authenticated.
    Object-level: admin (is_staff) OR the specialist whose profile is linked to the appointment.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        specialist_profile = getattr(request.user, "specialist_profile", None)
        return specialist_profile is not None and obj.specialist_id == specialist_profile.id


class IsAppointmentCanceller(BasePermission):
    """
    Object-level: admin, the appointment's customer (owner), or the assigned specialist.
    Covers all roles that may cancel an appointment.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if obj.user_id == request.user.id:
            return True
        specialist_profile = getattr(request.user, "specialist_profile", None)
        return specialist_profile is not None and obj.specialist_id == specialist_profile.id
