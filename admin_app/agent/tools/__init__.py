from .greeting import greeting
from .product_stock import (
    out_of_stock_products,
    low_stock_products,
    search_products,
    top_selling_products,
    update_product_stock,
    product_reviews,
    product_average_rating,
)
from .order_tools import (
    get_dashboard_summary,
    get_todays_orders,
    get_todays_sales,
    get_order,
    recent_orders,
    list_orders_by_status,
    update_order_status,
    get_customer_orders,
    revenue_over_period,
)
from .customer_tools import (
    get_customer,
    new_customers_since,
    unverified_users,
    top_customers,
)
from .analytics_tools import (
    product_count_by_brand,
    best_selling_brands,
    wishlist_count_by_product,
)
from .payment_tools import (
    payment_status_summary,
    failed_payments,
)

TOOLS = [
    greeting,
    get_dashboard_summary,
    get_todays_sales,
    get_todays_orders,
    get_order,
    recent_orders,
    list_orders_by_status,
    update_order_status,
    get_customer_orders,
    revenue_over_period,
    out_of_stock_products,
    low_stock_products,
    search_products,
    top_selling_products,
    update_product_stock,
    product_reviews,
    product_average_rating,
    get_customer,
    new_customers_since,
    unverified_users,
    top_customers,
    product_count_by_brand,
    best_selling_brands,
    wishlist_count_by_product,
    payment_status_summary,
    failed_payments,
]

TOOL_MAP = {
    tool.name: tool
    for tool in TOOLS
}

__all__ = [
    "TOOLS",
    "TOOL_MAP",
]
