from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from products.models import Mobile
from rest_framework.response import Response
from .models import Wishlist
from rest_framework.generics import ListAPIView
from .serializers import WishlistSerializer

# Create your views here.



#Add To Wishlist View
class AddToWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product')

        try:
            product = Mobile.objects.get(id=product_id)
        except Mobile.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        wishlist, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            return Response({"message": "Already in wishlist"}, status=200)

        return Response({"message": "Added to wishlist"}, status=201)
    




#WishList View
class WishlistView(ListAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')
    





#Remove Wishlist
class RemoveFromWishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, wishlist_id):
        try:
            wishlist = Wishlist.objects.get(
                id=wishlist_id,
                user=request.user
            )
            wishlist.delete()
            return Response({"message": "Removed from wishlist"}, status=200)

        except Wishlist.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)