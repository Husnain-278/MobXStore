from django.db.models import Count, Sum
from langchain_core.tools import tool

from payments.models import Payment


@tool
def payment_status_summary():
    """Return a summary of payments grouped by status (pending, completed, failed)."""

    rows = Payment.objects.values("status").annotate(
        count=Count("id"),
        total=Sum("amount"),
    )

    return [
        {
            "status": row["status"],
            "payment_count": row["count"],
            "total_amount": float(row["total"]) if row["total"] else 0,
        }
        for row in rows
    ]


@tool
def failed_payments(limit: int = 10):
    """Return the most recent failed payments."""

    payments = Payment.objects.filter(
        status="failed"
    ).order_by("-created_at")[:limit]

    return [
        {
            "payment_id": payment.pk,
            "order_id": payment.order.order_id,
            "customer": str(payment.order.user),
            "amount": float(payment.amount),
            "currency": payment.currency,
            "payer_email": payment.payer_email,
            "created_at": payment.created_at.isoformat(),
        }
        for payment in payments
    ]