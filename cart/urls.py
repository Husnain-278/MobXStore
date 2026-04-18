from django.urls import path
from .views import CartView, AddToCartView, RemoveCartView, UpdateCartView, OrderView, OrderHistoryView
urlpatterns = [
    path('', CartView.as_view()),
    path('add-to-cart/', AddToCartView.as_view()),
    path('remove/', RemoveCartView.as_view()),
    path('update/', UpdateCartView.as_view()),
    path("order/", OrderView.as_view()),
    path('orders/', OrderHistoryView.as_view()),
   
]
