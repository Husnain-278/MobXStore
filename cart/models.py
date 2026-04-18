from django.db import models
from django.contrib.auth import get_user_model
from products.models import Mobile
import uuid
# Create your models here.
User = get_user_model()


#Cart Model
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(Mobile, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Cart"



#Order Model
class Order(models.Model):
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    PAYMENT_METHOD_CHOICES = (
    ('cod', 'Cash on Delivery'),
    ('paypal', 'PayPal'),
    )

    PAYMENT_STATUS_CHOICES = (
      ('pending', 'Pending'),
      ('paid', 'Paid'),
      ('failed', 'Failed'),
      )


    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Mobile, on_delete=models.SET_NULL, null =True, blank=True)
    order_id = models.CharField(max_length=30,unique=True, editable=False)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_name =  models.CharField(max_length=299)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    address_line = models.TextField(null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Order {self.order_id} - {self.user.username}"
    



