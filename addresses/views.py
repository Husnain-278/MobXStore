from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AddressSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Address

# Create your views here.



class AddressListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AddressSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
    



class AddressDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            address = Address.objects.get(id=pk, user=request.user)
            address.delete()
            return Response({"message": "Deleted successfully"})
        except Address.DoesNotExist:
            return Response({"error": "Address not found"}, status=404)
        
        
        
        
        
        
class SetDefaultAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user

        Address.objects.filter(user=user, is_default=True).update(is_default=False)

        try:
            address = Address.objects.get(id=pk, user=user)
            address.is_default = True
            address.save()
            return Response({"message": "Default address set"})
        except Address.DoesNotExist:
            return Response({"error": "Address not found"}, status=404)