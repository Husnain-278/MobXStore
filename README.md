# MobXStore — Mobile E-Commerce API

MobXStore is a Django REST Framework backend for a mobile e-commerce store. It provides email-verified JWT accounts, a product catalogue, cart and wishlist management, saved addresses, order history, and PayPal checkout.

## Highlights

- Email verification and JWT bearer authentication
- Mobile catalogue with brands, categories, specifications, images, reviews, filtering, and pagination
- Single-product cart with stock-aware quantity updates
- Wishlist and saved-address management
- PayPal order creation and capture in USD
- Atomic paid-order creation: address snapshot, payment record, inventory reduction, cart clearing, and asynchronous confirmation email
- Status-specific admin emails for pending, processing, shipped, delivered, completed, and cancelled orders
- Duplicate PayPal captures return the original payment data instead of creating another order

## Tech stack

- Python 3.12, Django 6, and Django REST Framework
- PostgreSQL
- `uv` for dependency management
- Simple JWT for authentication
- PayPal Server SDK
- Celery and Redis for background emails
- Brevo for email delivery
- Cloudinary for product images

## Quick start

1. Create the local environment file and supply its values:

   ```bash
   cp .env.example .env
   ```

   Configure PostgreSQL, Cloudinary, Brevo, Redis, and PayPal. For local payment testing, use PayPal sandbox credentials:

   ```env
   PAYPAL_MODE=sandbox
   PAYPAL_CLIENT_ID=your-sandbox-client-id
   PAYPAL_CLIENT_SECRET=your-sandbox-client-secret
   PAYPAL_RETURN_URL=http://localhost:5173/payment/success
   PAYPAL_CANCEL_URL=http://localhost:5173/payment/cancel
   ```

2. Install dependencies and apply migrations:

   ```bash
   uv sync
   uv run python manage.py migrate
   ```

3. Start the API server:

   ```bash
   uv run python manage.py runserver
   ```

4. Start Redis and a Celery worker to deliver verification and order-confirmation emails:

   ```bash
   redis-server
   uv run celery -A store_backend worker -l info
   ```

Optional: seed the catalogue with fake data and images from `assets/`:

```bash
uv run python manage.py generate_fake_products --count 12 --category-count 6
```

## Authentication

1. `POST /api/accounts/register/` to create an inactive account and send a verification email.
2. Open `GET /api/accounts/verify-email/<uidb64>/<token>/` from that email.
3. `POST /api/accounts/login/` to receive `access` and `refresh` tokens.
4. Send authenticated requests with `Authorization: Bearer <access_token>`.

## API endpoints

All endpoints return the project response envelope, using `success`, `message`, `data`, and/or `errors` as applicable.

### Accounts — `/api/accounts/`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `register/` | Public | Register with `email` and `password`; sends verification email. |
| POST | `login/` | Public | Sign in with `email` and `password`; returns JWT tokens. |
| GET | `verify-email/<uidb64>/<token>/` | Public | Activate a verified email address. |
| GET | `profile/` | JWT | Retrieve the authenticated user profile. |

### Products — `/api/products/`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `brands/` | Public | List brands (paginated). |
| GET | `categories/` | Public | List categories (paginated). |
| GET | `mobiles/` | Public | List mobiles with filtering and pagination. |
| GET | `mobiles/<slug>/` | Public | Get a mobile, its specifications, images, reviews, and average rating. |
| POST | `add-review/` | JWT | Add a review for a purchased product. Body: `product_id`, `rating`, optional `comment`. |

`mobiles/` supports `brand`, `category`, `min_price`, `max_price`, `search`, and `ordering` (for example, `-price`).

### Cart and orders — `/api/cart/`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `` | JWT | Retrieve the current cart. |
| POST | `add-to-cart/` | JWT | Add a product. Body: `product_id`, optional `quantity`. |
| PATCH | `update/` | JWT | Adjust quantity. Body: `action` set to `increase` or `decrease`. |
| DELETE | `remove/` | JWT | Clear the current cart. |
| GET | `orders/` | JWT | List the authenticated user's order history, newest first. |

`POST /api/cart/order/` remains available for the legacy direct-order flow. New checkouts should use the PayPal endpoints below.

### Wishlist — `/api/wishlist/`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `` | JWT | List wishlist items. |
| POST | `add/` | JWT | Add a product. Body: `{ "product": <id> }`. |
| DELETE | `remove/<wishlist_id>/` | JWT | Remove a wishlist item. |

### Addresses — `/api/addresses/`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `` | JWT | List saved addresses. |
| POST | `` | JWT | Create an address. |
| DELETE | `delete/<pk>/` | JWT | Delete an address. |
| POST | `set-default/<pk>/` | JWT | Make an address the default. |

### Payments (PayPal) — `/api/payments/`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `create-order/` | JWT | Create a PayPal order from the current cart. Body: `{ "address_id": 1 }`. |
| POST | `capture-order/` | JWT | Capture an approved PayPal order. Body: `{ "paypal_order_id": "…", "address_id": 1 }`. |

## PayPal checkout flow

1. Add a product to the cart and create a saved address.
2. Call `POST /api/payments/create-order/` with that address ID. The response includes `paypal_order_id`, `approval_url`, `amount`, and `currency`.
3. Redirect the customer to `approval_url` to approve the payment in PayPal.
4. Call `POST /api/payments/capture-order/` with the PayPal order ID and address ID.

On a successful capture, the API verifies the completed PayPal amount against the cart total, creates an `Order` and one-to-one `Payment` record, marks the order as `processing` and paid, reduces stock, clears the cart, and queues an order-confirmation email. A repeated capture request for the same PayPal order returns its existing result.

## Models

| Model | Purpose |
|---|---|
| `User` | Email-based account; inactive until email verification. |
| `Brand`, `Category`, `Mobile` | Catalogue structure and mobile inventory. |
| `Specification`, `MobileSpecification`, `MobileImage` | Product attributes and Cloudinary-hosted images. |
| `Review` | One review per user and product. |
| `Cart` | One cart entry per user, containing one product and quantity. |
| `Address` | User-owned delivery addresses, including a default address. |
| `Order` | Purchased product details, price and address snapshots, fulfilment and payment status. |
| `Payment` | One-to-one PayPal transaction details for an order. |
| `Wishlist` | User-saved products. |

## Development notes

- API pagination defaults to 10 results per page, with a maximum of 100.
- CORS permits the configured Vite development origins; adjust `CORS_ALLOWED_ORIGINS` for deployment.
- Create an admin account with `uv run python manage.py createsuperuser`; payment records are available in Django admin.
- Changing an existing order's status in Django admin queues a customer notification through Celery after the database transaction succeeds.
- Keep `.env` out of version control and use production PayPal credentials only with `PAYPAL_MODE=production`.
