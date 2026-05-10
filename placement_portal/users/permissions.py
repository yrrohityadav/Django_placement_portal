# users/permissions.py
#
# WHY PERMISSIONS?
# ─────────────────────────────────────────────────────────────
# Authentication  = Who are you?   (JWT proves your identity)
# Authorization   = What can you do? (Permissions decide this)
#
# DRF has built-in permissions like IsAuthenticated.
# But our app also needs role-based rules:
#   - Only students can apply to jobs
#   - Only companies can create/edit jobs
#   - Admin can do everything
#
# We create custom permission classes by extending BasePermission
# and overriding has_permission(). If it returns True → access
# granted. If it returns False → DRF automatically returns 403.
# ─────────────────────────────────────────────────────────────

from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    """
    Allows access only to users with role == 'student'.

    Usage in a view:
        permission_classes = [IsAuthenticated, IsStudent]
    """
    # This message is shown when permission is denied
    message = "Access denied. Only students can perform this action."

    def has_permission(self, request, view):
        # request.user is set by JWTAuthentication after verifying the token
        # We check: is the user logged in AND is their role 'student'?
        return (
            request.user.is_authenticated
            and request.user.role == "student"
        )


class IsCompany(BasePermission):
    """
    Allows access only to users with role == 'company'.

    Usage in a view:
        permission_classes = [IsAuthenticated, IsCompany]
    """
    message = "Access denied. Only company accounts can perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "company"
        )


class IsAdminRole(BasePermission):
    """
    Allows access only to users with role == 'admin'.

    Note: This checks our CUSTOM 'role' field, not Django's is_staff flag.

    Usage in a view:
        permission_classes = [IsAuthenticated, IsAdminRole]
    """
    message = "Access denied. Admin only."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "admin"
        )
