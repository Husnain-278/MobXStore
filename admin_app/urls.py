from django.urls import path

from .views import (
    AdminLoginAPIView,
    AdminLogoutAPIView,
    AdminRefreshTokenAPIView,
    DashboardAPIView,
)

urlpatterns = [
    path("login/", AdminLoginAPIView.as_view(), name="admin-login"),
    path("logout/", AdminLogoutAPIView.as_view(), name="admin-logout"),
    path("token/refresh/", AdminRefreshTokenAPIView.as_view(), name="admin-token-refresh"),
    path("dashboard/", DashboardAPIView.as_view(), name="dashboard"),
]