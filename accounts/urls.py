from django.urls import path
from .views import RegisterView, CustomLoginView, ProfileView, EmailVerifyView
urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', CustomLoginView.as_view()),
    path('verify-email/<uidb64>/<token>/', EmailVerifyView.as_view()),
    path('profile/', ProfileView.as_view()),

]
