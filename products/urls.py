from django.urls import path
from .views import BrandView, CategoryView, MobileListView, MobileDetailView, AddReviewView



urlpatterns = [
    path('brands/', BrandView.as_view()),
    path('categories/', CategoryView.as_view()),
    path('mobiles/', MobileListView.as_view()),
    path('mobiles/<slug:slug>/', MobileDetailView.as_view()),
    path('add-review/', AddReviewView.as_view()),
]

