from .models import Cart, Order
from products.models import Mobile
from .serializers import CartSerializer, AddToCartSerializer, OrderSerializer, UpdateCartSerializer
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from products.pagination import DefaultPagination
from rest_framework import status
from .email_service import send_order_confirmation_email
# Create your views here.

#Cart View
class CartView(RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
       cart = Cart.objects.select_related('product').filter(user=self.request.user).first()
    
       if not cart:
         raise NotFound("Cart is empty.")
    
       return cart
    


#Add TO Cart
class AddToCartView(APIView):
   permission_classes = [IsAuthenticated]
   
   def post(self, request):
      serializer= AddToCartSerializer(data= request.data, context={'request': request})
      if serializer.is_valid():
         cart= serializer.save()
         return Response({
            "success": True,
            "data": CartSerializer(cart).data,
         },status=status.HTTP_201_CREATED)
      return Response({
         "success": False,
         "errors": serializer.errors,
      }, status.HTTP_400_BAD_REQUEST)
   


#Remove Cart
class RemoveCartView(APIView):
   permission_classes = [IsAuthenticated]

   def delete(self, request):
      cart = Cart.objects.get(user = request.user)
      if not cart:
         return Response({
            "message": "Cart already empty."
         }, status=status.HTTP_404_NOT_FOUND)
      cart.delete()
      return Response({
         "message": "Cart removed successfully!"
      }, status=status.HTTP_200_OK)
   

#Update Cart View
class UpdateCartView(APIView):
   permission_classes = [IsAuthenticated]

   def patch(self, request):
      serializer = UpdateCartSerializer(data = request.data, context={'request':request})

      if serializer.is_valid():
         cart = serializer.validated_data['cart']
         action = serializer.validated_data['action']

         if action == 'increase':
            cart.quantity += 1
         else:
            cart.quantity -= 1
         cart.save()

         return Response({
            "message": "Cart Updated successfully.",
            "data": CartSerializer(cart).data
         },status.HTTP_200_OK)
      
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
#Order View
class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            order = serializer.save()

            #  Use Celery to send email asynchronously
            send_order_confirmation_email.delay(order.user.id, order.id)

            return Response({
                "success": True,
                "message": "Order created successfully.",
                "data": {
                    "order_id": order.order_id,
                    "total_price": order.total_price
                }
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Something went wrong.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
        
        
#Order History View
class OrderHistoryView(ListAPIView):
   permission_classes = [IsAuthenticated]
   serializer_class = OrderSerializer
   pagination_class = DefaultPagination

   def get_queryset(self):
      return Order.objects.filter(user = self.request.user).order_by('-created_at')
   


