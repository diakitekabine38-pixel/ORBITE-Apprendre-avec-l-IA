from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsStudent(BasePermission):
    """Authenticated user with the student role."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.has_role("student"))


class IsInstructor(BasePermission):
    """Only a formateur can create/manage courses."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.has_role("instructor")
        )


class IsAdminUser(BasePermission):
    """Admin or super admin."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin()
        )


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_super_admin()
        )


class IsOwnerOrReadOnly(BasePermission):
    """Object-level: only the owner may modify the object."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = getattr(obj, "user", None)
        return bool(user and user == request.user)


class IsAdminOrInstructorOwner(BasePermission):
    """Object-level: admins may act on any course; instructors on their own."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_admin():
            return True
        return getattr(obj, "instructor_id", None) == request.user.id


class IsAdminOrOwner(BasePermission):
    """Admin may act on any object; the owner only on their own."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin():
            return True
        user = getattr(obj, "user", None)
        return bool(user and user == request.user)