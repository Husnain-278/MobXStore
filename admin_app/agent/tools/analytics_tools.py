from django.db.models import Count, Sum
from langchain_core.tools import tool

from products.models import Brand, Mobile
from wishlist.models import Wishlist


@tool
def product_count_by_brand():
    """Return how many products each brand has, ordered by count descending."""

    rows = (
        Brand.objects
        .annotate(product_count=Count("mobile"))
        .order_by("-product_count")
    )

    return [
        {
            "brand_name": brand.name,
            "product_count": brand.product_count,
        }
        for brand in rows
    ]


@tool
def best_selling_brands(limit: int = 5):
    """Return the brands with the highest total quantity sold."""

    rows = (
        Brand.objects
        .annotate(
            total_units=Sum("mobile__order__quantity"),
            order_count=Count("mobile__order"),
        )
        .order_by("-total_units")
        [:limit]
    )

    return [
        {
            "brand_name": brand.name,
            "total_units_sold": brand.total_units or 0,
            "order_count": brand.order_count,
        }
        for brand in rows
    ]


@tool
def wishlist_count_by_product(limit: int = 5):
    """Return the most wishlisted products as a popularity signal."""

    rows = (
        Mobile.objects
        .annotate(wishlist_count=Count("wishlist"))
        .filter(wishlist_count__gt=0)
        .order_by("-wishlist_count")[:limit]
    )

    return [
        {
            "product_id": product.pk,
            "product_name": product.name,
            "brand_name": product.brand.name,
            "wishlist_count": product.wishlist_count,
        }
        for product in rows
    ]