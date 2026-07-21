from django.urls import path

from .views import CreateOrderAPIView, CaptureOrderAPIView

urlpatterns = [
    path(
        "create-order/",
        CreateOrderAPIView.as_view(),
        name="create-order",
    ),
    path(
        "capture-order/",
        CaptureOrderAPIView.as_view(),
        name="capture-order",
    ),
]