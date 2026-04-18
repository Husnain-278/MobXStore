from rest_framework import serializers 
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


#Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only =True)
    class Meta:
        model = User
        fields = ['email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(email=validated_data["email"], password=validated_data["password"])
        return user
    


#Login Serializer
class CustomLoginSerializer(TokenObtainPairSerializer):
    username_field = 'email'



