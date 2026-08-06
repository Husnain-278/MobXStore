from django.urls import path

from admin_app.views import (
    AdminLoginView,
    AdminLogoutView,
    AdminRefreshView,
    AdminMeView,
    AdminDashboardView,
    ChatAPIView,
    ChatStreamAPIView,
    ConversationDeleteAPIView,
    ConversationListAPIView,
    MessageListAPIView,
)

app_name = "admin_app"

urlpatterns = [
    path(
        "auth/login/",
        AdminLoginView.as_view(),
        name="admin-login",
    ),
    path(
        "auth/logout/",
        AdminLogoutView.as_view(),
        name="admin-logout",
    ),
    path(
        "auth/refresh/",
        AdminRefreshView.as_view(),
        name="admin-refresh",
    ),
    path(
        "auth/me/",
        AdminMeView.as_view(),
        name="admin-me",
    ),
    path(
        "dashboard/summary/",
        AdminDashboardView.as_view(),
        name="admin-dashboard-summary",
    ),
    path(
        "chat/",
        ChatAPIView.as_view(),
        name="chat",
    ),
    path(
        "chat/stream/",
        ChatStreamAPIView.as_view(),
        name="chat-stream",
    ),
    path(
        "conversations/",
        ConversationListAPIView.as_view(),
        name="conversation-list",
    ),
    path(
        "conversations/<int:conversation_id>/",
        ConversationDeleteAPIView.as_view(),
        name="conversation-delete",
    ),
    path(
        "conversations/<int:conversation_id>/messages/",
        MessageListAPIView.as_view(),
        name="message-list",
    ),
]
