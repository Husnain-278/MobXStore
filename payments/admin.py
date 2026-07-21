from django.contrib import admin
from .models import Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'paypal_order_id', 'paypal_capture_id', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('paypal_order_id', 'paypal_capture_id', 'payer_email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Order Information', {
            'fields': ('order', 'amount', 'currency')
        }),
        ('PayPal Information', {
            'fields': ('paypal_order_id', 'paypal_capture_id', 'payer_email')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


admin.site.register(Payment, PaymentAdmin)
