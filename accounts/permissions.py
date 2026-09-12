"""Application roles are independent of Django staff/superuser capabilities."""

from rest_framework.permissions import BasePermission

from accounts.models import UserRole


def has_role(user, *roles):
    return bool(user and user.is_authenticated and user.role in roles)


def is_application_admin(user):
    return has_role(user, UserRole.OWNER, UserRole.ADMIN)


def get_specialist_profile(user):
    if not has_role(user, UserRole.SPECIALIST):
        return None
    return getattr(user, "specialist_profile", None)


class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return is_application_admin(request.user)


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return has_role(request.user, UserRole.CUSTOMER)
