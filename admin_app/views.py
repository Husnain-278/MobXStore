from rest_framework import status
from rest_framework.response import Response
from .permissions import IsSuperUser
from rest_framework.views import APIView
from django.conf import settings


from .cookies import set_auth_cookies, clear_auth_cookies, set_access_cookie
from .serializers import AdminLoginSerializer
from .services import AdminAuthService, AdminDashboardService
from .authentication import CookieJWTAuthentication



class AdminLoginAPIView(APIView):
    """"
    Authenticate an admin user and issue JWT cookies.
    """
    
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        
        auth_data = AdminAuthService.login(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )   
        
        response = Response(
            {
                "message": "Login successful.",
                "user":{
                    "id": auth_data["user"].id,
                    "email": auth_data["user"].email,
                    "first_name": auth_data["user"].first_name,
                    "last_name": auth_data["user"].last_name,
                },
            },
            status=status.HTTP_200_OK,
        )   
        
        set_auth_cookies(
            response= response,
            access_token= auth_data["access"],
            refresh_token= auth_data["refresh"],
        )
        
        return response
    
    

class AdminLogoutAPIView(APIView):
    """""
    Logout an admin user.
    """
    
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperUser]
    

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)
        
        AdminAuthService.logout(refresh_token)
        
        response = Response(
            {"message": "Logout successful."},
            status=status.HTTP_200_OK,
        )
        
        clear_auth_cookies(response)
        return response


class AdminMeAPIView(APIView):
    """Return the authenticated administrator's safe display information."""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperUser]

    def get(self, request):
        return Response(
            {
                "user": {
                    "id": request.user.id,
                    "email": request.user.email,
                    "first_name": request.user.first_name,
                    "last_name": request.user.last_name,
                }
            },
            status=status.HTTP_200_OK,
        )
    
    
class AdminRefreshTokenAPIView(APIView):
    """
    Refresh the access token using the provided refresh token.
    """
    
    authentication_classes = []
    permission_classes = []

    
    def post(self, request):
        
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)
        
        access_token = AdminAuthService.refresh_access_token(refresh_token)
        
        response = Response(
            {
                "message": "access token refreshed.",
            },
            status=status.HTTP_200_OK
        )
        
        set_access_cookie(response, access_token)
        
        return response
        
        
        
        
class DashboardAPIView(APIView):
    """
    Return dashboard summary.
    """

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsSuperUser]

    def get(self, request):
        
        data = AdminDashboardService.dashboard_summary()
        
        return Response(
            {
                "message": "Dashboard summary for the last 15 days.",
                "summary": data
            },
            status=status.HTTP_200_OK,
        )
