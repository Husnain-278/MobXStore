from django.contrib import admin
from django.db import transaction

from .email_service import send_order_status_update_email
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
		"payment_status",
		"created_at",
	)
	search_fields = ("order_id", "user__email", "product_name")
	list_filter = ("status", "payment_status", "created_at")

	def save_model(self, request, obj, form, change):
		"""Queue a status email only after an existing order changes status."""
		previous_status = None
		if change:
			previous_status = (
				Order.objects.filter(pk=obj.pk)
				.values_list("status", flat=True)
				.first()
			)

		super().save_model(request, obj, form, change)

		if previous_status and previous_status != obj.status:
			transaction.on_commit(
				lambda: send_order_status_update_email.delay(
					obj.user_id,
					obj.pk,
					previous_status,
				)
			)
