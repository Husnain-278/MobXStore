from django.contrib.auth import authenticate
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone
from cart.models import Order
from django.db.models import Count, Q

User = get_user_model()


class AdminAuthService:

    @staticmethod
    def login(email: str, password: str):
        """
        Authenticate an admin user and generate JWT tokens.
        """

        user = authenticate(
            email=email,
            password=password,
        )

        if user is None:
            raise exceptions.AuthenticationFailed("Invalid email or password.")

        if not user.is_active:
            raise exceptions.AuthenticationFailed("Your account is inactive.")

        if not user.is_staff:
            raise exceptions.PermissionDenied(
                "You are not authorized to access the admin panel."
            )

        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
        
    
    @staticmethod
    def logout(refresh_token: str):
        """"
        Blacklist the refresh token
        """
        
        if not refresh_token:
            raise exceptions.AuthenticationFailed("Refresh token not found.")
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            raise exceptions.AuthenticationFailed("Invalid refresh token.")
        
        
    @staticmethod
    def refresh_access_token(refresh_token: str):
        """
        refresh the access token using the provided refresh token
        """
        
        
        if not refresh_token:
            raise exceptions.AuthenticationFailed("Refresh token not found.")
        
        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            return access_token
        
        except Exception:
            raise exceptions.AuthenticationFailed("Invalid refresh token.")
        
        



class AdminDashboardService:

    @staticmethod
    def dashboard_summary():
        fifteen_days_ago = timezone.now() - timedelta(days=15)

        registered_users = User.objects.filter(
            date_joined__gte=fifteen_days_ago
        ).count()

        order_summary = Order.objects.aggregate(
            completed=Count(
                "id",
                filter=Q(
                    created_at__gte=fifteen_days_ago,
                    status="completed",
                ),
            ),
            pending=Count(
                "id",
                filter=Q(
                    created_at__gte=fifteen_days_ago,
                    status="pending",
                ),
            ),
            processing=Count(
                "id",
                filter=Q(
                    created_at__gte=fifteen_days_ago,
                    status="processing",
                ),
            ),
            shipped=Count(
                "id",
                filter=Q(
                    created_at__gte=fifteen_days_ago,
                    status="shipped",
                ),
            ),
            cancelled=Count(
                "id",
                filter=Q(
                    created_at__gte=fifteen_days_ago,
                    status="cancelled",
                ),
            ),
        )

        return {
            "registered_users": registered_users,
            "orders": order_summary,
        }