from django.urls import path

from admin_app.views import (
    ChatAPIView,
    ConversationDeleteAPIView,
    ConversationListAPIView,
    MessageListAPIView,
)

app_name = "admin_app"

urlpatterns = [
    path(
        "chat/",
        ChatAPIView.as_view(),
        name="chat",
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