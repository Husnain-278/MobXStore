from django.db import models
from products.models import Mobile
from accounts.models import User
# Create your models here.

#Wishlist model
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Mobile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"