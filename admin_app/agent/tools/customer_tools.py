from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone
from langchain_core.tools import tool

from cart.models import Order

User = get_user_model()


@tool
def get_customer(email: str):
    """Return the profile and store activity of a customer by their email address."""

    customer = User.objects.filter(email__iexact=email).first()

    if customer is None:
        return {"error": f"No customer found with email {email}."}

    return {
        "email": customer.email,
        "full_name": customer.get_full_name() or None,
        "phone": customer.phone,
        "is_active": customer.is_active,
        "is_staff": customer.is_staff,
        "joined_at": customer.created_at.isoformat(),
        "order_count": Order.objects.filter(user=customer).count(),
    }


@tool
def new_customers_since(days: int = 7):
    """Return customers who registered within the last N days."""

    days = max(1, min(days, 365))

    start_date = timezone.localdate() - timedelta(days=days - 1)

    customers = User.objects.filter(created_at__date__gte=start_date)

    return [
        {
            "email": customer.email,
            "full_name": customer.get_full_name() or None,
            "phone": customer.phone,
            "is_active": customer.is_active,
            "joined_at": customer.created_at.isoformat(),
        }
        for customer in customers.order_by("-created_at")
    ]


@tool
def unverified_users(limit: int = 20):
    """Return users who have not yet verified their email (is_active=False)."""

    users = User.objects.filter(
        is_active=False
    ).order_by("-created_at")[:limit]

    return [
        {
            "email": user.email,
            "full_name": user.get_full_name() or None,
            "phone": user.phone,
            "joined_at": user.created_at.isoformat(),
        }
        for user in users
    ]


@tool
def top_customers(limit: int = 5):
    """Return the customers with the most orders placed."""

    rows = (
        User.objects
        .annotate(order_count=Count("orders"))
        .filter(order_count__gt=0)
        .order_by("-order_count")[:limit]
    )

    return [
        {
            "email": customer.email,
            "full_name": customer.get_full_name() or None,
            "phone": customer.phone,
            "order_count": customer.order_count,
        }
        for customer in rows
    ]