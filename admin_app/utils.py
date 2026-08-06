from django.conf import settings
from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """Allow access only to superusers."""

    message = "Superuser privileges are required."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_superuser)


def set_admin_auth_cookies(response, access, refresh):
    response.set_cookie(
        settings.JWT_ACCESS_COOKIE,
        access,
        max_age=settings.JWT_ACCESS_COOKIE_MAX_AGE,
        path=settings.JWT_ACCESS_COOKIE_PATH,
        secure=settings.JWT_COOKIE_SECURE,
        httponly=settings.JWT_COOKIE_HTTP_ONLY,
        samesite=settings.JWT_COOKIE_SAMESITE,
    )
    response.set_cookie(
        settings.JWT_REFRESH_COOKIE,
        refresh,
        max_age=settings.JWT_REFRESH_COOKIE_MAX_AGE,
        path=settings.JWT_REFRESH_COOKIE_PATH,
        secure=settings.JWT_COOKIE_SECURE,
        httponly=settings.JWT_COOKIE_HTTP_ONLY,
        samesite=settings.JWT_COOKIE_SAMESITE,
    )


def clear_admin_auth_cookies(response):
    response.delete_cookie(
        settings.JWT_ACCESS_COOKIE,
        path=settings.JWT_ACCESS_COOKIE_PATH,
        samesite=settings.JWT_COOKIE_SAMESITE,
    )
    response.delete_cookie(
        settings.JWT_REFRESH_COOKIE,
        path=settings.JWT_REFRESH_COOKIE_PATH,
        samesite=settings.JWT_COOKIE_SAMESITE,
    )
