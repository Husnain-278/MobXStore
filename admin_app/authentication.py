from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class CookieJWTAuthentication(JWTAuthentication):
    """
    Authenticate users using the JWT stored in an HttpOnly cookie.
    """

    def authenticate(self, request):
        access_token = request.COOKIES.get(settings.JWT_ACCESS_COOKIE)

        if not access_token:
            return None

        try:
            validated_token = self.get_validated_token(access_token)
        except InvalidToken:
            return None

        return self.get_user(validated_token), validated_token