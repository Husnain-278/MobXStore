import json
import logging

from django.http import StreamingHttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_app.agent.ai_service import AIService
from admin_app.renderers import ServerSentEventRenderer
from admin_app.serializers.chat import ChatSerializer
from admin_app.services.conversation_service import ConversationService


logger = logging.getLogger(__name__)


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


class ChatStreamAPIView(APIView):
    """Stream chat replies as Server-Sent Events (SSE)."""

    permission_classes = [IsAuthenticated]
    renderer_classes = [ServerSentEventRenderer]

    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation = ConversationService.get_or_create(
            conversation_id=serializer.validated_data.get("conversation"),
            user=request.user,
        )

        def event_stream():
            # Named events make the protocol extensible while every payload
            # remains JSON, so clients never need to parse model text.
            yield self._sse_event(
                "message.started",
                {"conversation": conversation.id},
            )

            try:
                for event in AIService().stream_reply(
                    conversation=conversation,
                    user_input=serializer.validated_data["message"],
                ):
                    event_type = event.pop("type")
                    yield self._sse_event(event_type, event)
            except Exception:
                # Do not expose provider or internal implementation details to
                # the browser. Detailed errors should be captured in logging.
                logger.exception("Chat response streaming failed.")
                yield self._sse_event(
                    "error",
                    {
                        "code": "stream_generation_failed",
                        "message": "Unable to complete the chat response.",
                    },
                )

        response = StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream; charset=utf-8",
        )
        response["Cache-Control"] = "no-cache, no-transform"
        response["X-Accel-Buffering"] = "no"
        return response

    @staticmethod
    def _sse_event(event, data):
        payload = json.dumps(data, ensure_ascii=False, default=str)
        return f"event: {event}\ndata: {payload}\n\n"
