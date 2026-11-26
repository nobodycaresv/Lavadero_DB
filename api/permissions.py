from rest_framework.permissions import SAFE_METHODS, BasePermission


class LecturaPublicaEscrituraStaff(BasePermission):
    """Cualquiera puede consultar (GET); solo el personal puede crear o modificar."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or bool(request.user and request.user.is_staff)
