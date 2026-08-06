from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum

from cart.models import Order

User = get_user_model()

ORDER_STATUSES = [choice[0] for choice in Order.STATUS_CHOICES]


class DashboardService:

    @staticmethod
    def summary(days=15):
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)

        user_counts = dict(
            User.objects.filter(created_at__date__gte=start_date)
            .values("created_at__date")
            .annotate(count=Count("id"))
            .values_list("created_at__date", "count")
        )

        order_counts = {}
        order_rows = (
            Order.objects.filter(created_at__date__gte=start_date)
            .values("created_at__date", "status")
            .annotate(count=Count("id"))
        )
        for row in order_rows:
            day = row["created_at__date"]
            order_counts.setdefault(day, {})[row["status"]] = row["count"]

        daily = []
        for offset in range(days):
            day = start_date + timedelta(days=offset)
            by_status = {
                status: order_counts.get(day, {}).get(status, 0)
                for status in ORDER_STATUSES
            }
            daily.append(
                {
                    "date": day.isoformat(),
                    "orders": by_status,
                    "new_users": user_counts.get(day, 0),
                }
            )

        orders_by_status = {
            status: sum(entry["orders"][status] for entry in daily)
            for status in ORDER_STATUSES
        }

        revenue = Order.objects.filter(
            created_at__date__gte=start_date,
            payment_status="paid",
        ).aggregate(total=Sum("total_price"))["total"]

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days,
            "summary": {
                "total_orders": sum(orders_by_status.values()),
                "orders_by_status": orders_by_status,
                "total_revenue": str(revenue) if revenue is not None else "0.00",
                "new_users": sum(entry["new_users"] for entry in daily),
            },
            "daily": daily,
        }
