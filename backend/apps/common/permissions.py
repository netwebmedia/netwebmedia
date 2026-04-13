"""Role-based permission classes for organization-scoped views."""

from rest_framework import permissions

from apps.organizations.models import Membership


# Role hierarchy: higher index = more privilege
ROLE_HIERARCHY = {
    Membership.Role.VIEWER: 0,
    Membership.Role.MARKETING: 1,
    Membership.Role.SALES: 1,
    Membership.Role.OPERATIONS: 2,
    Membership.Role.MANAGER: 3,
    Membership.Role.ADMIN: 4,
    Membership.Role.OWNER: 5,
}

# Minimum role required for write operations per action
WRITE_ACTIONS = {"create", "update", "partial_update", "destroy"}
READ_ACTIONS = {"list", "retrieve"}


def _get_membership(request):
    return getattr(request, "_cached_membership", None)


def _has_minimum_role(membership, minimum_role):
    if membership is None:
        return False
    user_level = ROLE_HIERARCHY.get(membership.role, -1)
    required_level = ROLE_HIERARCHY.get(minimum_role, 999)
    return user_level >= required_level


class IsOrganizationMember(permissions.BasePermission):
    """Any active member of the organization can read. Denies if no membership."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        membership = _get_membership(request)
        return membership is not None and membership.is_active


class IsOrganizationViewer(permissions.BasePermission):
    """Read-only for viewers; write requires at least Sales/Marketing role."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        membership = _get_membership(request)
        if membership is None or not membership.is_active:
            return False
        action = getattr(view, "action", None)
        if action in READ_ACTIONS:
            return True
        if action in WRITE_ACTIONS:
            return _has_minimum_role(membership, Membership.Role.SALES)
        return True


class IsOrganizationManager(permissions.BasePermission):
    """Read for all members; write requires Manager or above."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        membership = _get_membership(request)
        if membership is None or not membership.is_active:
            return False
        action = getattr(view, "action", None)
        if action in READ_ACTIONS:
            return True
        if action in WRITE_ACTIONS:
            return _has_minimum_role(membership, Membership.Role.MANAGER)
        return True


class IsOrganizationAdmin(permissions.BasePermission):
    """Read for all members; write requires Admin or Owner."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        membership = _get_membership(request)
        if membership is None or not membership.is_active:
            return False
        action = getattr(view, "action", None)
        if action in READ_ACTIONS:
            return True
        if action in WRITE_ACTIONS:
            return _has_minimum_role(membership, Membership.Role.ADMIN)
        return True


class IsOrganizationOwner(permissions.BasePermission):
    """Only organization owners can perform any action."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        membership = _get_membership(request)
        if membership is None or not membership.is_active:
            return False
        return membership.role == Membership.Role.OWNER


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object-level: only the record owner (or org admin+) can modify."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        membership = _get_membership(request)
        if membership and _has_minimum_role(membership, Membership.Role.ADMIN):
            return True
        owner_field = getattr(obj, "owner", None) or getattr(obj, "author", None)
        if owner_field and hasattr(owner_field, "pk"):
            return owner_field.pk == request.user.pk
        return False
