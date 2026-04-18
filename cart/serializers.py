from .models import Cart, Order
from rest_framework import serializers
from products.models import Mobile
from django.db import transaction


#Cart Serializer
class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', decimal_places=2, max_digits=10, read_only=True)
    total_price = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = [ 'id', 'product', 'quantity','product_name','product_price','total_price', 'created_at']
    
    def get_total_price(self, obj):
        return obj.product.price * obj.quantity


    
#Add To Cart Serializer
class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)

    def validate(self, data):
        user = self.context['request'].user
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        
        if quantity <= 0:
            raise serializers.ValidationError('Quantity must be greater than 0.')
        
        try:
            #get product
            product = Mobile.objects.get(id = product_id)
        except Mobile.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        #Stock Check
        if quantity > product.stock:
           raise serializers.ValidationError("Not enough stock available.")
        
        data['product'] = product
        #Check Existing Cart
        cart = getattr(user, 'cart', None)

        if cart:
            if cart.product != product:
                raise serializers.ValidationError('You already have another product in cart. Remove it first.')
            if cart.quantity + quantity > product.stock:
                raise serializers.ValidationError("Exceeds available stock.")
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data['product']
        quantity = validated_data['quantity']

        cart = Cart.objects.filter(user=user).first()

        # Create new cart
        if not cart:
            cart = Cart.objects.create(
                user=user,
                product=product,
                quantity=quantity
            )
        else:
            cart.quantity += quantity
            cart.save()

        return cart



#Order Serializer
class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields =[
            'product', 'order_id','quantity', 'total_price','product_name', 'product_price', 'status', 'payment_method','payment_status','created_at'
        ]
        read_only_fields=[
            'total_price', 'product_name','product_price', 'payment_status', 'order_id', 'created_at', 'quantity', 'product'
        ]

    def validate(self, data):
        user  = self.context['request'].user
        #Check cart exist
        try:
            cart  = user.cart
        except Cart.DoesNotExist:
            raise serializers.ValidationError('Cart is empty.')
        
        if cart.product.stock < cart.quantity:
            raise serializers.ValidationError("Not enough stock to place order.")
        
        if data.get('payment_method') not in ['cod', 'paypal']:
            raise serializers.ValidationError('Invalid payment method.')
        
        
        if data.get('payment_method') == 'paypal':
           raise serializers.ValidationError("PayPal payment is coming soon.")
        data['cart'] = cart
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        cart = validated_data['cart']
        payment_method = validated_data['payment_method']
        
        if payment_method == 'cod':
            payment_status = 'pending'
        else:
            payment_status = 'pending'
        #Transection Start
        with transaction.atomic():
          #Lock Row
          product = Mobile.objects.select_for_update().get(pk = cart.product.pk)

          #Recheck Stock
          if product.stock < cart.quantity:
            raise serializers.ValidationError("Stock changed, Try again.")
          
          #Update Stock
          product.stock -= cart.quantity
          product.save(update_fields=['stock'])

          #Create Order
          order = Order.objects.create(
              user = user,
              product = product,
              product_name = product.name,
              product_price = product.price,
              quantity = cart.quantity,
              total_price = product.price * cart.quantity,
              payment_method = payment_method, 
              payment_status = payment_status
          )
          #Delete Cart
          cart.delete()
        return order
        



#Update Cart Serializer
class UpdateCartSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['increase', 'decrease'])
    
    def validate(self, data):
        action = data.get('action')
        user = self.context['request'].user
        cart = getattr(user, 'cart', None)
        if not cart:
            raise serializers.ValidationError("Cart is empty.")
        
        product = cart.product
        if action == 'increase':
            if cart.quantity + 1 > product.stock:
                 raise serializers.ValidationError("Not enough stock.")
        if action == 'decrease':
            if cart.quantity <= 1:
                raise serializers.ValidationError("Cannot reduce below 1.")
        data['cart'] = cart 
        return data
    




