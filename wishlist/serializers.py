from .models import Wishlist
from rest_framework import serializers


#Wishlist serializer
class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'created_at']
        read_only_fields = ['id', 'created_at']