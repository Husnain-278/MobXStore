import traceback

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import PayPalService
from .serializers import (
    CreateOrderSerializer,
    CaptureOrderSerializer,
)



class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            data = PayPalService.create_order(
                user=request.user,
                address_id=serializer.validated_data["address_id"],
            )

            return Response(
                {
                    "success": True,
                    "message": "PayPal order created successfully.",
                    "data": data,
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                    "errors": {"validation": str(e)},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            traceback.print_exc()

            return Response(
                {
                    "success": False,
                    "message": "Failed to create PayPal order.",
                    "errors": {"detail": str(e)},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
            

class CaptureOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CaptureOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            data = PayPalService.complete_checkout(
                user=request.user,
                paypal_order_id=serializer.validated_data["paypal_order_id"],
                address_id=serializer.validated_data["address_id"],
            )

            return Response(
                {
                    "success": True,
                    "message": "Payment captured successfully.",
                    "data": data,
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            return Response(
                {
                    "success": False,
                    "message": str(e),
                    "errors": {"validation": str(e)},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            traceback.print_exc()

            return Response(
                {
                    "success": False,
                    "message": "Failed to capture payment.",
                    "errors": {"detail": str(e)},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )