from datetime import datetime, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from langchain_core.tools import tool

from products.models import Mobile
from cart.models import Order
from django.contrib.auth import get_user_model
User = get_user_model()

ORDER_STATUSES = [choice[0] for choice in Order.STATUS_CHOICES]

def _serialize_order(order):
    return {
        "order_id": order.order_id,
        "customer": str(order.user),
        "product_name": order.product_name,
        "quantity": order.quantity,
        "total": float(order.total_price),
        "status": order.status,
        "payment_status": order.payment_status,
        "created_at": order.created_at.isoformat(),
    }

@tool
def get_todays_orders():
    """Return all orders created today."""
    today = timezone.localdate()

    orders = Order.objects.filter(
        created_at__date=today
    )

    return [
        {
            "order_id": order.order_id,
            "customer": str(order.user),
            "status": order.status,
            "total": float(order.total_price),
            "created_at": order.created_at.isoformat(),
        }
        for order in orders
    ]


@tool
def get_todays_sales():
    """Return today's sales summary."""

    today = timezone.localdate()

    orders = Order.objects.filter(
        created_at__date=today,
        status="completed",
    )

    total_sales = orders.aggregate(
        total=Sum("total_price")
    )["total"] or Decimal("0")

    return {
        "date": str(today),
        "orders_count": orders.count(),
        "total_sales": float(total_sales),
    }


@tool
def get_dashboard_summary():
    """Return a summary of important MobXStore dashboard statistics."""

    today = timezone.localdate()

    total_products = Mobile.objects.count()

    total_customers = User.objects.count()

    total_orders = Order.objects.count()

    todays_orders = Order.objects.filter(
        created_at__date=today
    ).count()

    pending_orders = Order.objects.filter(
        status="pending"
    ).count()

    out_of_stock_products = Mobile.objects.filter(
        stock__lte=0
    ).count()

    todays_sales = Order.objects.filter(
        created_at__date=today,
        status="completed",
    ).aggregate(
        total=Sum("total_price")
    )["total"] or Decimal("0")

    return {
        "total_products": total_products,
        "total_customers": total_customers,
        "total_orders": total_orders,
        "todays_orders": todays_orders,
        "todays_sales": float(todays_sales),
        "pending_orders": pending_orders,
        "out_of_stock_products": out_of_stock_products,
    }


@tool
def get_order(order_id: str):
    """Return the full details of a single order by its order id (e.g. "ORD-ABC12345")."""

    order = Order.objects.filter(order_id__iexact=order_id).first()

    if order is None:
        return {"error": f"No order found with id {order_id}."}

    return {
        **_serialize_order(order),
        "full_name": order.full_name,
        "phone": order.phone,
        "address_line": order.address_line,
        "city": order.city,
        "postal_code": order.postal_code,
        "country": order.country,
    }


@tool
def recent_orders(limit: int = 5):
    """Return the most recent orders, newest first."""

    orders = Order.objects.order_by("-created_at")[:limit]

    return [_serialize_order(order) for order in orders]


@tool
def list_orders_by_status(status: str):
    """Return all orders with the given status (pending, processing, shipped, delivered, completed, cancelled)."""

    if status not in ORDER_STATUSES:
        return {
            "error": f"Invalid status '{status}'. Valid statuses: {', '.join(ORDER_STATUSES)}."
        }

    orders = Order.objects.filter(status=status).order_by("-created_at")

    return [_serialize_order(order) for order in orders]


@tool
def update_order_status(order_id: str, status: str):
    """Update the status of an order by its order id (e.g. "ORD-ABC12345").

    Valid statuses: pending, processing, shipped, delivered, completed, cancelled.
    """

    if status not in ORDER_STATUSES:
        return {
            "error": f"Invalid status '{status}'. Valid statuses: {', '.join(ORDER_STATUSES)}."
        }

    order = Order.objects.filter(order_id__iexact=order_id).first()

    if order is None:
        return {"error": f"No order found with id {order_id}."}

    previous_status = order.status

    if previous_status == status:
        return {
            "order_id": order.order_id,
            "customer": str(order.user),
            "status": order.status,
            "payment_status": order.payment_status,
        }

    order.status = status
    order.save(update_fields=["status"])

    return {
        "order_id": order.order_id,
        "customer": str(order.user),
        "status": order.status,
        "payment_status": order.payment_status,
        "email_notified": previous_status != order.status,
    }


@tool
def get_customer_orders(email: str):
    """Return all orders placed by a customer, identified by their email address."""

    customer = User.objects.filter(email__iexact=email).first()

    if customer is None:
        return {"error": f"No customer found with email {email}."}

    orders = Order.objects.filter(
        user=customer
    ).order_by("-created_at")

    return [_serialize_order(order) for order in orders]


@tool
def revenue_over_period(days: int = 30):
    """Return the total revenue from paid orders over the last N days."""

    days = max(1, min(days, 365))

    start_date = timezone.localdate() - timedelta(days=days - 1)

    revenue = Order.objects.filter(
        created_at__date__gte=start_date,
        payment_status="paid",
    ).aggregate(total=Sum("total_price"))["total"] or Decimal("0")

    return {
        "start_date": str(start_date),
        "end_date": str(timezone.localdate()),
        "days": days,
        "total_revenue": float(revenue),
    }