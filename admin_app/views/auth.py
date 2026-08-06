from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from admin_app.authentication import AdminJWTAuthentication
from admin_app.serializers.auth import AdminLoginSerializer
from admin_app.utils import (
    IsSuperUser,
    clear_admin_auth_cookies,
    set_admin_auth_cookies,
)


def _auth_response(message, data=None, http_status=status.HTTP_200_OK):
    return Response(
        {
            "success": http_status < 400,
            "message": message,
            "data": data,
            "errors": None,
        },
        status=http_status,
    )


class AdminLoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = AdminLoginSerializer(
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Login failed!",
                    "data": None,
                    "errors": serializer.errors,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = _auth_response(
            "Login successful.",
            data={"email": serializer.validated_data["user"].email},
        )
        set_admin_auth_cookies(
            response,
            serializer.validated_data["access"],
            serializer.validated_data["refresh"],
        )
        return response


class AdminLogoutView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsSuperUser]

    def post(self, request):
        refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)

        if refresh:
            try:
                RefreshToken(refresh).blacklist()
            except TokenError:
                pass

        response = _auth_response("Logout successful.")
        clear_admin_auth_cookies(response)
        return response


class AdminRefreshView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)

        if not refresh:
            return Response(
                {
                    "success": False,
                    "message": "Refresh token not provided.",
                    "data": None,
                    "errors": {"refresh": ["Refresh token cookie is missing."]},
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            token = RefreshToken(refresh)
        except TokenError:
            response = _auth_response(
                "Invalid or expired refresh token.",
                http_status=status.HTTP_401_UNAUTHORIZED,
            )
            clear_admin_auth_cookies(response)
            return response

        access = str(token.access_token)
        new_refresh = str(token)

        response = _auth_response("Token refreshed.")
        set_admin_auth_cookies(response, access, new_refresh)
        return response


class AdminMeView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsSuperUser]

    def get(self, request):
        return _auth_response(
            "Admin profile fetched.",
            data={
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
            },
        )
