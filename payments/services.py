from decimal import Decimal

from cart.models import Cart, Order
from .paypal import paypal_client
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.conf import settings
from addresses.models import Address
from payments.models import Payment
from cart.email_service import send_order_confirmation_email



class PayPalService:

    @staticmethod
    def create_order(user, address_id):
        # 1. Validate Address
        address = get_object_or_404(
            Address,
            id=address_id,
            user=user,
        )
        
        # 2. Get Cart
        try:
            cart = Cart.objects.select_related("product").get(user=user)
        except Cart.DoesNotExist:
            raise ValueError("Cart is empty.")
        
        # 3. Validate Cart
        if not cart.product:
            raise ValueError("Cart product not found.")
        
        if cart.quantity <= 0:
            raise ValueError("Invalid cart quantity.")
        
        # 4. Validate Stock
        if cart.product.stock < cart.quantity:
            raise ValueError(f"Not enough stock. Available: {cart.product.stock}, Requested: {cart.quantity}")
        
        # 5. Calculate Total
        amount = Decimal(cart.product.price) * cart.quantity
        
        # 6. Create PayPal Order
        response = paypal_client.orders.create_order(
            {
                "body": {
                    "intent": "CAPTURE",
                    "purchase_units": [
                        {
                            "amount": {
                                "currency_code": "USD",
                                "value": str(amount),
                            }
                        }
                    ],
                    "application_context": {
                        "return_url": settings.PAYPAL_RETURN_URL,
                        "cancel_url": settings.PAYPAL_CANCEL_URL,
                        "user_action": "PAY_NOW",
                    },
                },
            }
        )
        
        approval_url = None
        
        for link in response.body.links:
            if link.rel == "approve":
                approval_url = link.href
                break
        
        return {
            "paypal_order_id": response.body.id,
            "status": response.body.status,
            "approval_url": approval_url,
            "amount": str(amount),
            "currency": "USD",
        }
        
    @staticmethod
    def capture_order(paypal_order_id):
        try:
            response = paypal_client.orders.capture_order(
                {
                    "id": paypal_order_id,
                }
            )
            if not response or not response.body:
                raise ValueError("PayPal API returned empty response.")
            return response
        except Exception as e:
            raise ValueError(f"Failed to capture PayPal order: {str(e)}")
        
        
    
    @staticmethod
    @transaction.atomic
    def complete_checkout(user, paypal_order_id, address_id):
        # 1. Capture PayPal Payment
        response = PayPalService.capture_order(paypal_order_id)
        
        if response.body.status != "COMPLETED":
            raise ValueError("Payment was not completed.")
        
        # 2. Verify status == COMPLETED
        # (Already done above)
        
        # 3. Check duplicate Payment (Idempotency)
        existing_payment = Payment.objects.filter(
            paypal_order_id=response.body.id
        ).first()
        
        if existing_payment:
            return {
                "order_id": existing_payment.order.order_id,
                "paypal_order_id": existing_payment.paypal_order_id,
                "paypal_capture_id": existing_payment.paypal_capture_id,
                "payment_status": existing_payment.status,
                "amount": str(existing_payment.amount),
            }
        
        # 4. Load Address
        address = get_object_or_404(
            Address,
            id=address_id,
            user=user,
        )
        
        # 5. Load Cart
        try:
            cart = Cart.objects.select_related("product").get(user=user)
        except Cart.DoesNotExist:
            raise ValueError("Cart not found. Please add products to cart before paying.")
        
        product = cart.product
        
        # 6. Validate Product Stock
        if product.stock < cart.quantity:
            raise ValueError(
                f"Not enough stock available. Available: {product.stock}, Requested: {cart.quantity}"
            )
        
        # 7. Calculate Total
        total = Decimal(product.price) * cart.quantity
        
        # 8. Compare PayPal Amount == Cart Amount
        purchase_unit = response.body.purchase_units[0]
        capture = purchase_unit.payments.captures[0]
        paypal_amount = Decimal(capture.amount.value)
        
        if paypal_amount != total:
            raise ValueError(
                f"Amount mismatch. PayPal: {paypal_amount}, Cart: {total}"
            )
        
        # 9. Create Order
        order = Order.objects.create(
            user=user,
            product=product,
            quantity=cart.quantity,
            total_price=total,
            product_name=product.name,
            product_price=product.price,
            status="processing",
            payment_status="paid",
            full_name=address.full_name,
            phone=address.phone,
            address_line=address.address_line,
            city=address.city,
            postal_code=address.postal_code,
            country=address.country,
        )
        
        # 10. Create Payment
        payer_email = None
        
        if response.body.payer:
            payer_email = response.body.payer.email_address
        
        payment = Payment.objects.create(
            order=order,
            paypal_order_id=response.body.id,
            paypal_capture_id=capture.id,
            amount=Decimal(capture.amount.value),
            currency=capture.amount.currency_code,
            payer_email=payer_email,
            status="completed",
        )
        
        # 11. Reduce Stock
        product.stock -= cart.quantity
        product.save(update_fields=["stock"])
        
        # 12. Delete Cart
        cart.delete()
        
        # 13. transaction.on_commit() - Send Confirmation Email & Analytics
        transaction.on_commit(
            lambda: send_order_confirmation_email.delay(user.id, order.id)
        )
        
        # 14. Return Success Response
        return {
            "order_id": order.order_id,
            "paypal_order_id": response.body.id,
            "paypal_capture_id": capture.id,
            "status": order.status,
            "order_status": order.status,
            "payment_status": order.payment_status,
            "amount": str(total),
        }