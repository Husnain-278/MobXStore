from django.db import models
from cart.models import Order
# Create your models here.


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )
    
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
    )
    paypal_order_id = models.CharField(
        max_length = 100,
        blank = True,
        null = True
    )
    paypal_capture_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    currency = models.CharField(
        max_length=10,
        default="USD",
    )
    payer_email = models.EmailField(
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.paypal_order_id