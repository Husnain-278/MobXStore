from django.db import transaction
from django.shortcuts import get_object_or_404

from admin_app.models import Conversation


class ConversationService:

    @staticmethod
    def create(user):
        return Conversation.objects.create(user=user)

    @staticmethod
    def get(conversation_id, user):
        return get_object_or_404(
            Conversation,
            id=conversation_id,
            user=user,
        )

    @staticmethod
    def list(user):
        return Conversation.objects.filter(user=user)

    @staticmethod
    @transaction.atomic
    def delete(conversation):
        conversation.delete()

    @staticmethod
    def update_title(conversation, title):
        conversation.title = title
        conversation.save(update_fields=["title"])
        return conversation
    
    
    @staticmethod
    def get_or_create(conversation_id, user):
        """
        Return an existing conversation or create a new one.
        """
        if conversation_id:
            return ConversationService.get(
                conversation_id=conversation_id,
                user=user,
            )

        return ConversationService.create(user=user)