from django.contrib import admin
from .models import Cart, Order


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "product", "quantity", "created_at")
	search_fields = ("user__email", "product__name")
	list_filter = ("created_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = (
		"order_id",
		"user",
		"product_name",
		"quantity",
		"total_price",
		"status",
		"payment_method",
		"payment_status",
		"created_at",
	)
	search_fields = ("order_id", "user__email", "product_name")
	list_filter = ("status", "payment_method", "payment_status", "created_at")
