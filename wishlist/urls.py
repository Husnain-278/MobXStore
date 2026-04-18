from django.urls import path
from .views import WishlistView, AddToWishlistView, RemoveFromWishlistView



urlpatterns = [
    path('', WishlistView.as_view()),
    path('add/', AddToWishlistView.as_view()),
    path('remove/<int:wishlist_id>/', RemoveFromWishlistView.as_view()),
]