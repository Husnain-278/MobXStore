from langchain_core.tools import tool
from django.db.models import Avg, Count, Sum
from products.models import Mobile, Review


@tool
def out_of_stock_products():
    """Return all products whose stock is equal to 0 or less than 5."""

    zero_stock_products = Mobile.objects.filter(
        stock__lte = 5
    ).values_list(
        "name",
        "brand__name",
        "stock"
    )

    return [
        {
            "product_name": product_name,
            "brand_name": brand_name,
            "stock": stock,
        }
        for product_name, brand_name, stock in zero_stock_products
    ]


@tool
def low_stock_products(threshold: int = 5):
    """Return all products whose stock is less than or equal to the given threshold."""

    products = Mobile.objects.filter(
        stock__lte=threshold
    ).values_list(
        "name",
        "brand__name",
        "stock",
    )

    return [
        {
            "product_name": product_name,
            "brand_name": brand_name,
            "stock": stock,
        }
        for product_name, brand_name, stock in products
    ]


@tool
def search_products(query: str):
    """Search products by name or brand name. Returns matching products with price and stock."""

    products = Mobile.objects.filter(
        name__icontains=query
    ) | Mobile.objects.filter(
        brand__name__icontains=query
    ).distinct()

    return [
        {
            "product_id": product.pk,
            "product_name": product.name,
            "brand_name": product.brand.name,
            "price": float(product.price),
            "stock": product.stock,
        }
        for product in products
    ]


@tool
def top_selling_products(limit: int = 5):
    """Return the top selling products by total quantity ordered."""

    rows = (
        Mobile.objects
        .annotate(
            total_units=Sum("order__quantity"),
            order_count=Count("order"),
        )
        .order_by("-total_units")
        [:limit]
    )

    return [
        {
            "product_id": product.pk,
            "product_name": product.name,
            "brand_name": product.brand.name,
            "total_units_sold": product.total_units or 0,
            "order_count": product.order_count,
        }
        for product in rows
    ]


@tool
def update_product_stock(product_id: int, stock: int):
    """Update the stock quantity of a product by its numeric id. Returns the updated product."""

    if stock < 0:
        return {"error": "Stock cannot be negative."}

    updated = Mobile.objects.filter(pk=product_id).update(stock=stock)

    if not updated:
        return {"error": f"No product found with id {product_id}."}

    product = Mobile.objects.get(pk=product_id)

    return {
        "product_id": product.pk,
        "product_name": product.name,
        "brand_name": product.brand.name,
        "stock": product.stock,
    }


@tool
def product_reviews(product_id: int):
    """Return reviews for a product by its numeric id, ordered newest first."""

    product = Mobile.objects.filter(pk=product_id).first()

    if product is None:
        return {"error": f"No product found with id {product_id}."}

    reviews = Review.objects.filter(
        product=product
    ).order_by("-created_at")

    return [
        {
            "review_id": review.pk,
            "customer": str(review.user),
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at.isoformat(),
        }
        for review in reviews
    ]


@tool
def product_average_rating(product_id: int):
    """Return the average rating of a product by its numeric id."""

    product = Mobile.objects.filter(pk=product_id).first()

    if product is None:
        return {"error": f"No product found with id {product_id}."}

    result = Review.objects.filter(product=product).aggregate(
        average=Avg("rating"),
        count=Count("id"),
    )

    return {
        "product_id": product.pk,
        "product_name": product.name,
        "average_rating": float(result["average"]) if result["average"] else None,
        "review_count": result["count"],
    }