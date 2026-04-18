
from rest_framework import serializers
from .models import  Address



class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['user']
    
    def create(self, validated_data):
       user = self.context['request'].user

       if validated_data.get('is_default'):
          Address.objects.filter(user=user, is_default=True).update(is_default=False)

       return Address.objects.create(user=user, **validated_data)