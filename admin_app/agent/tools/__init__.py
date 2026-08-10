from .greeting import greeting
from .product_stock import out_of_stock_products

TOOLS = [
    greeting,
    out_of_stock_products,
]

TOOL_MAP = {
    tool.name: tool
    for tool in TOOLS
}

__all__ = [
    "TOOLS",
    "TOOL_MAP",
]
