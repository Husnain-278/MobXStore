# PayPal Payment Flow - Quick Start Guide

## Prerequisites
1. PostgreSQL running
2. Redis running (`redis-server`)
3. Celery worker running
4. PayPal sandbox credentials configured in `.env`

## Environment Setup

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update `.env` with your PayPal sandbox credentials:
```env
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_secret
```

3. Run migrations (if not already done):
```bash
uv run python manage.py migrate
```

## Running the Application

### Terminal 1: Start Django Server
```bash
cd /home/dev-husnain/Django/MobXStore/MobXStore
uv run python manage.py runserver
```

### Terminal 2: Start Celery Worker
```bash
cd /home/dev-husnain/Django/MobXStore/MobXStore
uv run celery -A store_backend worker -l info
```

### Terminal 3: Redis (if not running)
```bash
redis-server
```

## Testing the Payment Flow

### Step 1: Create User Account
```bash
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d {
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }
```

### Step 2: Login
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d {
    "email": "test@example.com",
    "password": "testpass123"
  }
```

Save the `access` token from response.

### Step 3: Create/Get Address
```bash
curl -X POST http://localhost:8000/api/addresses/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d {
    "full_name": "John Doe",
    "phone": "+923001234567",
    "address_line": "123 Main St",
    "city": "Karachi",
    "postal_code": "75500",
    "country": "Pakistan"
  }
```

Note the `address_id` from response.

### Step 4: Get Products
```bash
curl http://localhost:8000/api/products/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Note a `product_id`.

### Step 5: Add Product to Cart
```bash
curl -X POST http://localhost:8000/api/cart/add-to-cart/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d {
    "product_id": 1,
    "quantity": 1
  }
```

### Step 6: Create PayPal Order
```bash
curl -X POST http://localhost:8000/api/payments/create-order/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d {
    "address_id": 1
  }
```

Response:
```json
{
  "success": true,
  "message": "PayPal order created successfully.",
  "data": {
    "paypal_order_id": "5O190127TN364715T",
    "status": "CREATED",
    "approval_url": "https://www.sandbox.paypal.com/...",
    "amount": "999.99",
    "currency": "USD"
  }
}
```

1. Open `approval_url` in browser
2. Login with PayPal sandbox account
3. Review and approve payment

### Step 7: Capture Payment
```bash
curl -X POST http://localhost:8000/api/payments/capture-order/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d {
    "paypal_order_id": "5O190127TN364715T",
    "address_id": 1
  }
```

Response:
```json
{
  "success": true,
  "message": "Payment captured successfully.",
  "data": {
    "order_id": "ORD-A1B2C3D4",
    "paypal_order_id": "5O190127TN364715T",
    "paypal_capture_id": "3C679366P0238559L",
    "payment_status": "completed",
    "amount": "999.99"
  }
}
```

### Step 8: Verify in Database
```bash
# Check Order was created
uv run python manage.py shell
>>> from cart.models import Order
>>> Order.objects.last()

# Check Payment was created
>>> from payments.models import Payment
>>> Payment.objects.last()

# Check Stock was reduced
>>> from products.models import Mobile
>>> Mobile.objects.get(id=1).stock  # Should be reduced by quantity
```

### Step 9: Check Celery Email Task
In Celery worker terminal, you should see:
```
[2026-07-15 12:00:00,000: INFO/MainProcess] Task cart.email_service.send_order_confirmation_email[...] received
[2026-07-15 12:00:00,100: INFO/ForkPoolWorker-1] Task cart.email_service.send_order_confirmation_email[...] succeeded
```

## Admin Interface

Access Django admin at: `http://localhost:8000/admin/`

Admin credentials: (create superuser if needed)
```bash
uv run python manage.py createsuperuser
```

Then:
1. Go to `Payments > Payments`
2. View payment details including PayPal order/capture IDs
3. Filter by status
4. Search by PayPal IDs

## Idempotency Test

Call capture endpoint again with same paypal_order_id:
```bash
curl -X POST http://localhost:8000/api/payments/capture-order/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d {
    "paypal_order_id": "5O190127TN364715T",
    "address_id": 1
  }
```

Should return same order data (no duplicate payment created).

## Troubleshooting

### PayPal Connection Error
- Verify `PAYPAL_CLIENT_ID` and `PAYPAL_CLIENT_SECRET` in `.env`
- Check `PAYPAL_MODE=sandbox` for testing
- Verify internet connection

### Cart Empty Error
- Ensure product was added to cart before create-order
- Check cart endpoint: `GET /api/cart/`

### Stock Error
- Verify product has sufficient stock
- Check product details in admin

### Email Not Sent
- Verify Celery worker is running
- Check Brevo API key in settings
- Check Celery logs for errors

### Address Not Found
- Verify address was created and belongs to user
- Check address ID matches: `GET /api/addresses/`
