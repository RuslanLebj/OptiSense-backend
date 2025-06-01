from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey


class CustomPermission(BasePermission):
    """
    Пропускает запрос, если:
    -пользователь аутентифицирован (JWT, session и т. д.)
    или
    -передан валидный API-ключ (заголовок `Authorization: Api-Key <value>`).
    """

    def has_permission(self, request, view):
        return IsAuthenticated().has_permission(
            request, view
        ) or HasAPIKey().has_permission(request, view)