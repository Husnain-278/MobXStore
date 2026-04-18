from rest_framework.generics import ListAPIView, RetrieveAPIView
from .serializers import BrandSerializer, CategorySerializer, MobileListSerializer, MobileDetailSerializer, AddReviewSerializer
from .models import Brand, Category, Mobile,Review
from rest_framework import status
from rest_framework.response import Response
from .pagination import DefaultPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import MobileFilter
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
# Create your views here.


#List All Brands
class BrandView(ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class  = DefaultPagination
    

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "success": True,
                "message": "Brands fetched",
                "data": serializer.data,
                "errors": None,
            })
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Brands fetched",
            "data": serializer.data,
            "errors": None,
        }, status.HTTP_200_OK)

    

#List ALL Categories
class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = DefaultPagination
    
    def list(self, request, *args,**kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many = True)
            return self.get_paginated_response({
            "success": True,
            "message": "Categories fetched",
            "data": serializer.data,
            "errors": None,
        })
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Categories fetched",
            "data": serializer.data,
            "errors": None,
        }, status.HTTP_200_OK)
    



#List Mobiles
class MobileListView(ListAPIView):
    pagination_class = DefaultPagination
    def get_queryset(self):
        return Mobile.objects.select_related('brand', 'category').all()
    serializer_class = MobileListSerializer
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MobileFilter
    search_fields = ['name']
    ordering_fields = ['price']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many= True, context={'request': request})
            return self.get_paginated_response({
                "success": True,
                "message": "Mobiles fetched",
                "data": serializer.data,
                "errors": None,
            })
        serializer = self.get_serializer(queryset, many=True, context = {'request': request})
        return Response({
            "success": True,
            "message": "Mobiles fetched",
            "data": serializer.data,
            "errors": None,
        }, status.HTTP_200_OK)
    



#Mobile Detail View
class MobileDetailView(RetrieveAPIView):
    queryset = Mobile.objects.select_related('brand', 'category').prefetch_related('images', 'specs', 'reviews__user')
    serializer_class = MobileDetailSerializer
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return Response({
            "success": True,
            "message": "Mobile Detail fetched",
            "data": serializer.data,
            "errors": None,
        }, status.HTTP_200_OK)
    



#Add Review View
class AddReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddReviewSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            #  Get product
            try:
                product = Mobile.objects.get(
                    id=serializer.validated_data['product_id']
                )
            except Mobile.DoesNotExist:
                return Response({
                    "success": False,
                    "message": "Product not found",
                    "data": None,
                    "errors": {"product_id": "Invalid product"}
                }, status=status.HTTP_404_NOT_FOUND)

            #  Create review
            review = Review.objects.create(
                user=request.user,
                product=product,
                rating=serializer.validated_data['rating'],
                comment=serializer.validated_data.get('comment', '')
            )

            return Response({
                "success": True,
                "message": "Review added successfully",
                "data": {
                    "id": review.id,
                    "product": review.product.id,
                    "rating": review.rating,
                    "comment": review.comment,
                    "created_at": review.created_at
                },
                "errors": None
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "message": "Review not added",
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)