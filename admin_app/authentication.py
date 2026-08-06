from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class AdminJWTAuthentication(JWTAuthentication):
    """Authenticate admin requests using the access token stored in an
    HTTP-only cookie instead of the Authorization header.

    Only superusers are allowed through this backend.
    """

    def authenticate(self, request):
        token = request.COOKIES.get(settings.JWT_ACCESS_COOKIE)

        if not token:
            return None

        request.META["HTTP_AUTHORIZATION"] = f"Bearer {token}"

        try:
            user_auth_tuple = super().authenticate(request)
        except InvalidToken:
            raise AuthenticationFailed(
                "Invalid or expired admin access token.",
                code="invalid_admin_token",
            )

        if user_auth_tuple is None:
            return None

        user, _ = user_auth_tuple

        if not user.is_superuser:
            raise AuthenticationFailed(
                "Superuser privileges are required.",
                code="superuser_required",
            )

        return user_auth_tuple
