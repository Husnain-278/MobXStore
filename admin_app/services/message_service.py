from admin_app.models import Message


class MessageService:

    @staticmethod
    def create_user_message(conversation, content):
        """
        Save a user message.
        """
        return Message.objects.create(
            conversation=conversation,
            role=Message.Role.USER,
            content=content,
        )

    @staticmethod
    def create_assistant_message(conversation, content):
        """
        Save an assistant message.
        """
        return Message.objects.create(
            conversation=conversation,
            role=Message.Role.ASSISTANT,
            content=content,
        )



    @staticmethod
    def list(conversation):
        """
        Return all messages in chronological order.
        """
        return conversation.messages.all()

    @staticmethod
    def get_recent(conversation, limit=20):
        """
        Return the latest messages in chronological order.
        """
        messages = list(
            conversation.messages
            .order_by("-created_at")[:limit]
        )

        messages.reverse()

        return messages

    @staticmethod
    def delete_all(conversation):
        """
        Delete all messages in a conversation.
        """
        conversation.messages.all().delete()
        
        
    @staticmethod
    def get_first_user_message(conversation):
        """
        Return the first user message in the conversation.
        """
        return (
            conversation.messages
            .filter(role=Message.Role.USER)
            .order_by("created_at")
            .first()
        )