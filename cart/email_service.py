from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Order

User = get_user_model()


@shared_task(bind=True, max_retries=3)
def send_order_confirmation_email(self, user_id, order_id):
    try:
        user = User.objects.get(id=user_id)
        order = Order.objects.get(id=order_id)

        subject = "Order Confirmation"

        message = f"""
Hi {user.first_name or 'Customer'},

Your order #{order.id} has been placed successfully.

Total Amount: {order.total_price}

Thank you for shopping with us!
"""

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False
        )

    except Exception as e:
        raise self.retry(exc=e, countdown=5)
    
    
    