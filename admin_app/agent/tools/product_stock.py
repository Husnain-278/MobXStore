from langchain_core.tools import tool
from products.models import Mobile


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