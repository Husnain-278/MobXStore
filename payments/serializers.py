from rest_framework import serializers


class CaptureOrderSerializer(serializers.Serializer):
    paypal_order_id = serializers.CharField()
    address_id = serializers.IntegerField()
    
    
    
class CreateOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
