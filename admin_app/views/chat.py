from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_app.agent.ai_service import AIService
from admin_app.serializers.chat import ChatSerializer
from admin_app.services.conversation_service import ConversationService


class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation = ConversationService.get_or_create(
            conversation_id=serializer.validated_data.get("conversation"),
            user=request.user,
        )

        ai_service = AIService()

        ai_message = ai_service.generate_reply(
            conversation=conversation,
            user_input=serializer.validated_data["message"],
        )

        return Response(
            {
                "conversation": conversation.id,
                "message": ai_message.content,
            },
            status=status.HTTP_200_OK,
        )