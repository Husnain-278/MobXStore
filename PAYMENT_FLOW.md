# PayPal Payment Flow Documentation

## Overview
This project implements a complete PayPal payment flow with only PayPal as the payment method. The flow consists of three main steps:
1. Create PayPal Order
2. Customer Approves on PayPal
3. Capture Payment

## API Endpoints

### 1. Create PayPal Order
**Endpoint:** `POST /api/payments/create-order/`

**Request:**
```json
{
    "address_id": 1
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "PayPal order created successfully.",
    "data": {
        "paypal_order_id": "5O190127TN364715T",
        "status": "CREATED",
        "approval_url": "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token=...",
        "amount": "999.99",
        "currency": "USD"
    }
}
```

**Response (Error):**
```json
{
    "success": false,
    "message": "Error message here",
    "errors": {
        "validation": "Detailed error"
    }
}
```

**Validations:**
- Address must exist and belong to the authenticated user
- Cart must exist for the user
- Product must have sufficient stock
- Cart quantity must be positive

### 2. Capture PayPal Order
**Endpoint:** `POST /api/payments/capture-order/`

**Request:**
```json
{
    "paypal_order_id": "5O190127TN364715T",
    "address_id": 1
}
```

**Response (Success):**
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

**Response (Error - Duplicate Payment):**
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

## Database Models

### Payment Model
- `order` (OneToOneField to Order)
- `paypal_order_id` (CharField)
- `paypal_capture_id` (CharField)
- `amount` (DecimalField)
- `currency` (CharField, default="USD")
- `payer_email` (EmailField)
- `status` (CharField, choices: "pending", "completed", "failed")
- `created_at` (DateTimeField)
- `updated_at` (DateTimeField)

### Order Model Updates
The Order model now has:
- `payment_status` (CharField, choices: "pending", "paid", "failed")
- Payment information is stored in the Payment model via OneToOneField

## Complete Checkout Flow

```
Frontend                Backend                PayPal
   │                      │                       │
   ├──────Create Order───>│                       │
   │                      │                       │
   │                      ├──────API Call────────>│
   │                      │<──────Order ID────────┤
   │                      │                       │
   │<──Approval URL───────┤                       │
   │                      │                       │
   │──Redirect to PayPal──────────────────────────>│
   │                      │                       │
   │<───────Approve───────────────────────────────┤
   │                      │                       │
   │──Capture Order──────>│                       │
   │                      │                       │
   │                      ├──Capture API────────>│
   │                      │<──Confirmed────────────┤
   │                      │                       │
   │                      ├─ Validate Address     │
   │                      ├─ Validate Cart        │
   │                      ├─ Validate Stock       │
   │                      ├─ Check Duplicate      │
   │                      ├─ Create Order         │
   │                      ├─ Create Payment       │
   │                      ├─ Reduce Stock         │
   │                      ├─ Delete Cart          │
   │                      ├─ Send Email (Celery)  │
   │                      │                       │
   │<────Success Result───┤                       │
```

## Detailed Checkout Steps

### Step 1: Create PayPal Order
1. Validate Address (must exist and belong to user)
2. Get Cart (must exist for user)
3. Validate Cart (product and quantity checks)
4. Validate Stock (ensure sufficient inventory)
5. Calculate Total (product price × quantity)
6. Create PayPal Order via API
7. Extract approval URL from response

### Step 2: Customer Approves
- Frontend redirects user to PayPal approval URL
- Customer logs in and approves payment on PayPal

### Step 3: Capture Payment (in complete_checkout)
1. Capture PayPal Payment
2. Verify status == "COMPLETED"
3. Check duplicate Payment (Idempotency - prevents double charging)
4. Load Address
5. Load Cart
6. Validate Product Stock
7. Calculate Total
8. Compare PayPal Amount == Cart Amount
9. Create Order (with order_id auto-generated)
10. Create Payment (store PayPal transaction details)
11. Reduce Stock
12. Delete Cart
13. Send Confirmation Email (async via Celery)
14. Return Success Response

## Required Environment Variables

Add these to your `.env` file:

```env
# PayPal Configuration
PAYPAL_MODE=sandbox                    # or "production"
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_client_secret
PAYPAL_RETURN_URL=http://localhost:5173/payment/success
PAYPAL_CANCEL_URL=http://localhost:5173/payment/cancel
```

## Error Handling

### Validation Errors (400)
- Empty or invalid cart
- Product not found
- Insufficient stock
- Invalid address
- Amount mismatch between PayPal and cart

### Payment Errors (400)
- PayPal API failures
- Payment not completed on PayPal
- Duplicate payment detection (returns 201 with existing order data)

### Business Logic
- If a duplicate payment is detected, the endpoint returns the existing order data (idempotency)
- All stock updates are locked to prevent race conditions
- Transactions are atomic - all or nothing

## Email Notifications

After successful payment capture:
1. Order confirmation email is sent asynchronously via Celery
2. Email includes:
   - Order ID
   - Order total
   - Delivery address
   - Product details

## Testing the Flow

### Prerequisites
1. Ensure PayPal sandbox credentials are configured
2. Ensure Redis is running (for Celery)
3. Ensure PostgreSQL is running
4. User must have an address created

### Test Steps
1. Add a product to cart via `/api/cart/add-to-cart/`
2. Create PayPal order via `/api/payments/create-order/`
3. Redirect to approval_url
4. Approve on PayPal sandbox
5. Capture payment via `/api/payments/capture-order/`
6. Verify order created in database
7. Verify payment record created
8. Verify stock reduced
9. Verify cart deleted
10. Verify email sent (check Celery logs)

## Admin Interface

Access the Payment model via Django admin at `/admin/payments/payment/`

Features:
- View all payments
- Filter by status and date
- Search by PayPal order/capture ID
- Read-only access to timestamps
