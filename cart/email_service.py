from celery import shared_task
from django.contrib.auth import get_user_model

from store_backend.email_service import send_email

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

        send_email(subject, message, user.email)

    except Exception as e:
        raise self.retry(exc=e, countdown=5)
    
    
    