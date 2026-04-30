from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.rol == "admin")


class IsAdminOrTecnicoRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol in {"admin", "tecnico"}
        )


class IsOwnerOrStaffRole(BasePermission):
    owner_field = "solicitante"

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.rol in {"admin", "tecnico"}:
            return True

        return getattr(obj, self.owner_field, None) == request.user
