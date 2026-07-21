from celery import shared_task
from django.contrib.auth import get_user_model

from store_backend.email_service import send_email

from .models import Order

User = get_user_model()


ORDER_STATUS_EMAILS = {
    "pending": {
        "subject": "We're preparing your order",
        "message": (
            "We've received your order and will begin processing it shortly. "
            "We'll email you again when it is on its way."
        ),
    },
    "processing": {
        "subject": "Your order is being prepared",
        "message": (
            "Our team is preparing your items for dispatch. "
            "We'll let you know as soon as your order has shipped."
        ),
    },
    "shipped": {
        "subject": "Good news — your order has shipped",
        "message": (
            "Your order is on its way. Please keep an eye on your phone and email "
            "for delivery updates."
        ),
    },
    "delivered": {
        "subject": "Your order has been delivered",
        "message": (
            "Your order has been marked as delivered. We hope you enjoy your purchase! "
            "If there is any issue with the delivery, please contact our support team."
        ),
    },
    "completed": {
        "subject": "Your order is complete",
        "message": (
            "Your order has been completed. Thank you for shopping with us — "
            "we'd love to see you again soon."
        ),
    },
    "cancelled": {
        "subject": "Your order has been cancelled",
        "message": (
            "Your order has been cancelled. If you did not request this change "
            "or have questions about a refund, please contact our support team."
        ),
    },
}


@shared_task(bind=True, max_retries=3)
def send_order_confirmation_email(self, user_id, order_id):
    try:
        user = User.objects.get(id=user_id)
        order = Order.objects.get(id=order_id)

        subject = "Order Confirmation"

        message = f"""
Hi {user.first_name or 'Customer'},

Your order #{order.order_id} has been placed successfully.

Total Amount: {order.total_price}

Thank you for shopping with us!
"""

        send_email(subject, message, user.email)

    except Exception as e:
        raise self.retry(exc=e, countdown=5)


@shared_task(bind=True, max_retries=3)
def send_order_status_update_email(self, user_id, order_id, previous_status):
    """Notify a customer after an administrator changes an order's status."""
    try:
        user = User.objects.get(id=user_id)
        order = Order.objects.get(id=order_id)

        status_label = order.get_status_display()
        previous_status_label = dict(Order.STATUS_CHOICES).get(
            previous_status,
            previous_status.replace("_", " ").title(),
        )
        status_email = ORDER_STATUS_EMAILS.get(
            order.status,
            {
                "subject": f"Order status update: {status_label}",
                "message": "Your order status has been updated.",
            },
        )
        subject = f"{status_email['subject']} — Order {order.order_id}"
        message = f"""
Hi {user.first_name or 'Customer'},

{status_email['message']}

Order #{order.order_id} changed from {previous_status_label} to {status_label}.

Order total: {order.total_price}

Thank you for shopping with us!
"""

        send_email(subject, message, user.email)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
