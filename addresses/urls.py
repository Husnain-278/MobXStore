from django.urls import path
from .views import AddressListCreateView, AddressDeleteView, SetDefaultAddressView

urlpatterns = [
    path('', AddressListCreateView.as_view()),
    path('delete/<int:pk>/', AddressDeleteView.as_view()),
    path('set-default/<int:pk>/', SetDefaultAddressView.as_view()),
]
