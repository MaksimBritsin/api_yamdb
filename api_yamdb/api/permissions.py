from rest_framework import permissions
from users.enums import UserRole


class AdminUserOrReadOnly(permissions.BasePermission):
    """Разрешает безопасные запросы всем пользователям.
    Изменение доступно только аутентифицированным администраторам.
    """
    message = (f"Доступно только для всех пользователей с безопасными "
               f"запросами или аутентифицированных пользователей с ролью "
               f"{UserRole.admin} для остальных запросов.")

    def has_permission(self, request, view):
        """Разрешает доступ для безопасных методов или администраторов."""
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class AdminPermission(permissions.BasePermission):
    """Доступ разрешён только администраторам и суперпользователям."""
    message = f"Доступно только для пользователей с ролью {UserRole.admin}"

    def has_permission(self, request, view):
        """Проверяет, является ли пользователь
          администратором или суперпользователем."""
        if request.user.is_authenticated:
            return request.user.is_admin or request.user.is_superuser
        return False


class IsAuthorModeratorOrReadOnly(permissions.BasePermission):
    """Разрешает редактирование автору, модератору или администратору.
    Остальным пользователям доступен только просмотр.
    """

    def has_permission(self, request, view):
        """Разрешает доступ для безопасных методов или
            аутентифицированных пользователей."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Разрешает редактирование автору, модератору или администратору."""
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_admin
                or request.user.is_moderator)
