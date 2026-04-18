from rest_framework import serializers
from .models import Brand, Category, Mobile, MobileImage, MobileSpecification, Review
from cart.models import Order
from django.db.models import Avg

#Brand Serializer
class BrandSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    class Meta:
        model  = Brand
        fields = ['id', 'name', 'logo', 'slug']
    def get_logo(self, obj):
        if obj.logo:
            return obj.logo.url
        return None


#Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


#Mobile List Serializer
class MobileListSerializer(serializers.ModelSerializer):
    brand = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    primary_image = serializers.SerializerMethodField()
    class Meta:
        model = Mobile
        fields = ['id', 'name', 'brand', 'category','price', 'slug', 'stock' , 'primary_image']

    def get_primary_image(self, obj):
        if obj.primary_image:
            return obj.primary_image.url 
        return None

class MobileImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = MobileImage
        fields = ['id', 'image']
    def get_image(self, obj):
       request = self.context.get('request')
       if obj.image:
          return request.build_absolute_uri(obj.image.url)
       return None


class MobileSpecificationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source = 'specification.name')
    class Meta: 
        model = MobileSpecification
        fields = ['name', 'value']



#Review Serializer
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']



#Mobile Detail Serialzier
class MobileDetailSerializer(serializers.ModelSerializer):
    brand = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    images = MobileImageSerializer(many=True, read_only=True)
    specifications = MobileSpecificationSerializer(source='specs', many=True, read_only=True)

    primary_image = serializers.SerializerMethodField()

    # ✅ New Fields
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    def get_primary_image(self, obj):
        request = self.context.get('request')
        if obj.primary_image:
            return request.build_absolute_uri(obj.primary_image.url)
        return None

    #  Average Rating
    def get_average_rating(self, obj):
        return obj.reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    #  Total Reviews
    def get_total_reviews(self, obj):
        return obj.reviews.count()

    #  Latest Reviews
    def get_reviews(self, obj):
        reviews = obj.reviews.select_related('user').order_by('-created_at')[:5]
        return ReviewSerializer(reviews, many=True).data

    class Meta:
        model = Mobile
        fields = [
            'id',
            'name',
            'slug',
            'stock',
            'price',
            'description',
            'primary_image',
            'brand',
            'category',
            'images',
            'specifications',
            'created_at',

            # New Fields
            'average_rating',
            'total_reviews',
            'reviews',
        ]


#Add Review Serializer
class AddReviewSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    rating = serializers.IntegerField()
    comment = serializers.CharField(required=False)

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def validate(self, data):
        user = self.context['request'].user
        product_id = data['product_id']

        #  Already reviewed?
        if Review.objects.filter(user=user, product_id=product_id).exists():
            raise serializers.ValidationError({
                "review": "You already reviewed this product"
                  })

        #  Check if user purchased this product
        

        has_purchased = Order.objects.filter(
            user=user,
            product_id=product_id,
            status='completed'
        ).exists()

        if not has_purchased:
            raise serializers.ValidationError(
                "You can only review products you have purchased"
            )

        return data



