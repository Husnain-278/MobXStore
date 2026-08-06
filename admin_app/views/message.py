from rest_framework.response import Response
from rest_framework.views import APIView

from admin_app.authentication import AdminJWTAuthentication
from admin_app.serializers.message import MessageSerializer
from admin_app.services.conversation_service import ConversationService
from admin_app.services.message_service import MessageService
from admin_app.utils import IsSuperUser


class MessageListAPIView(APIView):
    authentication_classes = [AdminJWTAuthentication]
    permission_classes = [IsSuperUser]

    def get(self, request, conversation_id):
        conversation = ConversationService.get(
            conversation_id=conversation_id,
            user=request.user,
        )

        messages = MessageService.list(conversation)

        serializer = MessageSerializer(
            messages,
            many=True,
        )

        return Response(serializer.data)