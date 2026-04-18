from rest_framework.views import APIView
from .serializers import RegisterSerializer, CustomLoginSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from .tokens import email_verification_token
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator

# Create your views here.

token_generator = PasswordResetTokenGenerator()
User = get_user_model()

class RegisterView(APIView):
    permission_classes = []
    def post(self, request):
        serializer = RegisterSerializer(data = request.data)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Registration Failed!",
                "data": None,
                "errors": serializer.errors
            }, status.HTTP_400_BAD_REQUEST)
        #save user
        user = serializer.save()
        
        #Generate uid
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        #Generate token
        token = email_verification_token.make_token(user)
        
        #Verfication URL
        verification_url = f"http://127.0.0.1:8000/api/accounts/verify-email/{uid}/{token}/"

        send_mail(
            subject="Verify your Account",
            message=f"Click the link to verify your account: \n {verification_url}",
            from_email=None,
            recipient_list=[user.email],
        )

        return Response({
            "success":True,
            "message": "Account created. Please check your email box to verify your account.",
            "data": None, 
            "errors": None
        }, status.HTTP_201_CREATED)





#Email Verify
class EmailVerifyView(APIView):
    permission_classes = []
    def get(self, request, uidb64, token):
        try:
            #Decoded UID
            uid = force_str(urlsafe_base64_decode(uidb64))

            #Get User
            user = User.objects.get(pk = uid)
            
        except(User.DoesNotExist, TypeError, ValueError, OverflowError):
            return Response({
                "success": False,
                "message": "Invalid verification link!",
                "data": None,
                "errors": None
            }, status.HTTP_400_BAD_REQUEST
            )
        
        if email_verification_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({
                "success": True,
                "message": "Email verified Successfully!",
                "data": None,
                "errors": None
            }, status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": "Invalid or expired verification link!",
            "data": None,
            "errors": None
        }, status.HTTP_400_BAD_REQUEST)




#Login View
class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomLoginSerializer
    




#Profile View
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        return Response({
            "success": True,
            "message": "User Profile Fetched!",
            "data": {
                "email": request.user.email,
                
            }
        },status.HTTP_200_OK)





