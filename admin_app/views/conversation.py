from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_app.serializers.conversation import ConversationSerializer
from admin_app.services.conversation_service import ConversationService


class ConversationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conversations = ConversationService.list(request.user)

        serializer = ConversationSerializer(
            conversations,
            many=True,
        )

        return Response(serializer.data)


class ConversationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, conversation_id):
        conversation = ConversationService.get(
            conversation_id=conversation_id,
            user=request.user,
        )

        ConversationService.delete(conversation)

        return Response(status=status.HTTP_204_NO_CONTENT)