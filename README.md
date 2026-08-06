# MobXStore — Mobile E-Commerce API

## Overview

- **Mobile e-commerce backend** built with Django 6 + Django REST Framework, PostgreSQL, and `uv`.
- **Email-verified JWT accounts** — users register, verify their email, then log in to receive access/refresh tokens.
- **Product catalogue** with brands, categories, specifications, image galleries, reviews, filtering, search, ordering, and pagination.
- **Shopping features** — cart, wishlist, saved addresses, and order history with status/payment tracking.
- **PayPal checkout** (sandbox/production) — order creation, approval URL, capture, and idempotent payment handling.
- **Async email delivery** via Celery + Redis and Brevo/Sendinblue.
- **Cloudinary-hosted product images** — no local media storage.
- **Superuser admin API** (`/api/admin/`) — cookie-based JWT auth, dashboard analytics, and an AI chat agent (Mistral) with tool support.

## Tech stack

- Python 3.12, Django 6, Django REST Framework 3.17+
- PostgreSQL
- `uv` for dependency management
- `djangorestframework-simplejwt` — JWT Bearer auth
- Celery + Redis — async email delivery
- Brevo (Sendinblue) — transactional emails
- Cloudinary — product image hosting
- PayPal Server SDK — order creation & capture (USD)
- `django-filter` — product filtering
- `django-cors-headers` — CORS for Vite dev server
- LangChain + Mistral AI — admin chat agent (`admin_app`)

## Setup guide

### Prerequisites

- Python 3.12+
- PostgreSQL running
- Redis running (for Celery email tasks)
- Cloudinary account (for product images)
- Brevo / Sendinblue API key (for emails)
- PayPal Developer account (sandbox credentials for local testing)
- Mistral API key (for the admin AI chat agent)

### 1. Clone and enter the project

```bash
git clone <repo-url> && cd MobXStore
```

### 2. Configure environment

Copy the example file:

```bash
cp .env.example .env
```

Edit `.env` with your values. Every variable is documented below:

#### Django

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`) | — |
| `DEBUG` | Enable debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | `localhost,127.0.0.1` |

#### JWT

| Variable | Description | Default |
|---|---|---|
| `ACCESS_TOKEN_LIFETIME_MINUTES` | Access token expiry in minutes | `60` |
| `REFRESH_TOKEN_LIFETIME_DAYS` | Refresh token expiry in days | `1` |

#### Database (PostgreSQL)

| Variable | Description | Default |
|---|---|---|
| `DB_ENGINE` | Django database engine | `django.db.backends.postgresql` |
| `DB_NAME` | Database name | `mobxstore_db` |
| `DB_USER` | Database user | `mobxstore_user` |
| `DB_PASSWORD` | Database password | — |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |

#### Cloudinary

| Variable | Description | Default |
|---|---|---|
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | — |
| `CLOUDINARY_API_KEY` | Cloudinary API key | — |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | — |

#### Email / Brevo

| Variable | Description | Default |
|---|---|---|
| `EMAIL_BACKEND` | Email backend class | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | SMTP host | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_USE_TLS` | Use TLS | `True` |
| `EMAIL_HOST_USER` | SMTP user | — |
| `EMAIL_HOST_PASSWORD` | SMTP password | — |
| `DEFAULT_FROM_EMAIL` | Sender address | `MobStoreX <noreply@example.com>` |
| `BREVO_API_KEY` | Brevo API key | — |
| `DEFAULT_FROM_NAME` | Sender display name | `Carvo` |

#### Celery

| Variable | Description | Default |
|---|---|---|
| `CELERY_BROKER_URL` | Redis broker URL | `redis://localhost:6379/0` |

#### PayPal

| Variable | Description | Default |
|---|---|---|
| `PAYPAL_MODE` | `sandbox` or `production` | `sandbox` |
| `PAYPAL_CLIENT_ID` | PayPal client ID | — |
| `PAYPAL_CLIENT_SECRET` | PayPal client secret | — |
| `PAYPAL_RETURN_URL` | Redirect after PayPal approval | `http://localhost:5173/payment/success` |
| `PAYPAL_CANCEL_URL` | Redirect if user cancels | `http://localhost:5173/payment/cancel` |

#### Admin AI chat (Mistral)

| Variable | Description | Default |
|---|---|---|
| `MISTRAL_API_KEY` | Mistral API key (used by the admin chat agent) | — |
| `MISTRAL_MODEL` | Mistral model name | `mistral-small-2506` |
| `MISTRAL_TEMPERATURE` | Sampling temperature | `0.3` |

### 3. Install dependencies

```bash
uv sync
```

### 4. Apply migrations

```bash
uv run python manage.py migrate
```

### 5. Start the server

```bash
uv run python manage.py runserver
```

The API is now available at `http://localhost:8000/api/`.

### 6. Start Celery (for emails)

```bash
redis-server
uv run celery -A store_backend worker -l info
```

### 7. (Optional) Seed fake data

```bash
uv run python manage.py generate_fake_products --count 12 --category-count 6
```

This uploads images from `assets/` to Cloudinary.

### 8. Create an admin (optional)

```bash
uv run python manage.py createsuperuser
```

Orders and payments are visible in Django admin at `/admin/`. A superuser is also required to access the admin API (`/api/admin/`) documented in [Part 2](#part-2--admin-app-apiadmin).

---

# Part 1 — Customer API (`/api/`)

The customer-facing API covers accounts, products, cart, wishlist, addresses, and payments.

## Authentication flow

All authenticated customer endpoints require `Authorization: Bearer <access_token>`.

1. **Register** — `POST /api/accounts/register/` creates an inactive account and sends a verification email.
2. **Verify email** — Open the link from the email: `GET /api/accounts/verify-email/<uidb64>/<token>/`.
3. **Login** — `POST /api/accounts/login/` returns JWT `access` and `refresh` tokens.
4. **Authenticate** — Pass the access token as `Authorization: Bearer <token>`.

Token refresh uses SimpleJWT defaults at `/api/token/refresh/`.

## API reference

All endpoints return the standard response envelope:

```json
{
    "success": true,
    "message": "Human-readable message",
    "data": { ... },
    "errors": null
}
```

On errors, `success` is `false` and `errors` contains validation details.

Paginated endpoints (brands, categories, mobiles, orders) wrap the envelope inside DRF's pagination structure:

```json
{
    "count": 25,
    "next": "http://localhost:8000/api/products/brands/?page=2",
    "previous": null,
    "results": {
        "success": true,
        "message": "...",
        "data": [ ... ],
        "errors": null
    }
}
```

Pagination defaults to 10 per page, max 100. Use `?page=<n>&page_size=<m>`.

---

### Accounts — `/api/accounts/`

---

#### `POST /api/accounts/register/`

Create a new account. The user is created with `is_active=False` — they must verify their email before logging in.

**Request:**
```json
{
    "email": "user@example.com",
    "password": "secure-password-123"
}
```

**Response `201`:** (no data)
```json
{
    "success": true,
    "message": "Account created. Please check your email box to verify your account.",
    "data": null,
    "errors": null
}
```

**Response `400`:** (validation error)
```json
{
    "success": false,
    "message": "Registration Failed!",
    "data": null,
    "errors": {
        "email": ["Enter a valid email address."]
    }
}
```

---

#### `POST /api/accounts/login/`

Authenticate and receive JWT tokens. Uses a custom serializer with `email` as the username field.

**Request:**
```json
{
    "email": "user@example.com",
    "password": "secure-password-123"
}
```

**Response `200`:**
```json
{
    "access": "eyJ0eXAiOiJKV1Qi...",
    "refresh": "eyJ0eXAiOiJKV1Qi..."
}
```

> The login response does **not** wrap data in the standard envelope — it returns SimpleJWT's default token response.

**Response `401`:**
```json
{
    "detail": "No active account found with the given credentials"
}
```

---

#### `GET /api/accounts/verify-email/<uidb64>/<token>/`

Activate an account via the link sent in the verification email.

**Response `200`:**
```json
{
    "success": true,
    "message": "Email verified Successfully!",
    "data": null,
    "errors": null
}
```

**Response `400`:**
```json
{
    "success": false,
    "message": "Invalid or expired verification link!",
    "data": null,
    "errors": null
}
```

---

#### `GET /api/accounts/profile/`

**Auth:** Bearer token

Returns the authenticated user's profile.

**Response `200`:**
```json
{
    "success": true,
    "message": "User Profile Fetched!",
    "data": {
        "email": "user@example.com"
    },
    "errors": null
}
```

---

### Products — `/api/products/`

---

#### `GET /api/products/brands/`

**Auth:** Public

List all brands (paginated).

**Query params:** `?page=1&page_size=10`

**Response `200`:**
```json
{
    "count": 6,
    "next": null,
    "previous": null,
    "results": {
        "success": true,
        "message": "Brands fetched",
        "data": [
            {
                "id": 1,
                "name": "Samsung",
                "logo": "https://res.cloudinary.com/...",
                "slug": "samsung"
            }
        ],
        "errors": null
    }
}
```

---

#### `GET /api/products/categories/`

**Auth:** Public

List all categories (paginated).

**Query params:** `?page=1&page_size=10`

**Response `200`:**
```json
{
    "results": {
        "success": true,
        "message": "Categories fetched",
        "data": [
            {
                "id": 1,
                "name": "Flagship",
                "slug": "flagship"
            }
        ],
        "errors": null
    },
    "count": 6,
    "next": null,
    "previous": null
}
```

---

#### `GET /api/products/mobiles/`

**Auth:** Public

List mobiles with filtering, search, ordering, and pagination.

**Query params:**

| Param | Type | Description |
|---|---|---|
| `brand` | string | Filter by brand slug (partial match) |
| `category` | string | Filter by category slug (partial match) |
| `min_price` | number | Minimum price (inclusive) |
| `max_price` | number | Maximum price (inclusive) |
| `search` | string | Search in mobile name |
| `ordering` | string | `price` or `-price` (descending) |
| `page` | int | Page number |
| `page_size` | int | Results per page (max 100) |

**Response `200`:**
```json
{
    "results": {
        "success": true,
        "message": "Mobiles fetched",
        "data": [
            {
                "id": 1,
                "name": "Galaxy S25",
                "brand": "Samsung",
                "category": "Flagship",
                "price": "999.99",
                "slug": "galaxy-s25",
                "stock": 15,
                "primary_image": "https://res.cloudinary.com/..."
            }
        ],
        "errors": null
    },
    "count": 12,
    "next": "http://localhost:8000/api/products/mobiles/?page=2",
    "previous": null
}
```

---

#### `GET /api/products/mobiles/<slug:slug>/`

**Auth:** Public

Get a single mobile with full details: specifications, image gallery, reviews, average rating.

**Response `200`:**
```json
{
    "success": true,
    "message": "Mobile Detail fetched",
    "data": {
        "id": 1,
        "name": "Galaxy S25",
        "slug": "galaxy-s25",
        "stock": 15,
        "price": "999.99",
        "description": "Full product description...",
        "primary_image": "http://localhost:8000/...",
        "brand": "Samsung",
        "category": "Flagship",
        "images": [
            {
                "id": 1,
                "image": "http://localhost:8000/..."
            }
        ],
        "specifications": [
            {
                "name": "RAM",
                "value": "12GB"
            },
            {
                "name": "Storage",
                "value": "256GB"
            }
        ],
        "created_at": "2026-07-28T12:00:00+05:00",
        "average_rating": 4.5,
        "total_reviews": 2,
        "reviews": [
            {
                "id": 1,
                "user": "user@example.com",
                "rating": 5,
                "comment": "Great phone!",
                "created_at": "2026-07-28T12:30:00+05:00"
            }
        ]
    },
    "errors": null
}
```

---

#### `POST /api/products/add-review/`

**Auth:** Bearer token

Add a review for a product the user has purchased (only one review per user per product).

**Request:**
```json
{
    "product_id": 1,
    "rating": 5,
    "comment": "Excellent phone!"
}
```

`comment` is optional.

**Response `201`:**
```json
{
    "success": true,
    "message": "Review added successfully",
    "data": {
        "id": 1,
        "product": 1,
        "rating": 5,
        "comment": "Excellent phone!",
        "created_at": "2026-07-28T12:35:00+05:00"
    },
    "errors": null
}
```

**Response `400`:**
```json
{
    "success": false,
    "message": "Review not added",
    "data": null,
    "errors": {
        "review": ["You already reviewed this product"]
    }
}
```

---

### Cart — `/api/cart/`

Cart is a `OneToOneField` to `User` — only **one** product entry per cart (quantity is adjustable).

---

#### `GET /api/cart/`

**Auth:** Bearer token

Retrieve the current cart.

**Response `200`:**
```json
{
    "success": true,
    "message": null,
    "data": {
        "id": 1,
        "product": 1,
        "quantity": 2,
        "product_name": "Galaxy S25",
        "product_price": "999.99",
        "total_price": "1999.98",
        "created_at": "2026-07-28T12:00:00+05:00"
    },
    "errors": null
}
```

**Response `404`:** (empty cart)
```json
{
    "detail": "Cart is empty."
}
```

Note: the 404 response does **not** follow the standard envelope.

---

#### `POST /api/cart/add-to-cart/`

**Auth:** Bearer token

Add a product to the cart. If a cart already exists with a different product, it is rejected (must remove first).

**Request:**
```json
{
    "product_id": 1,
    "quantity": 1
}
```

`quantity` defaults to `1`.

**Response `201`:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "product": 1,
        "quantity": 2,
        "product_name": "Galaxy S25",
        "product_price": "999.99",
        "total_price": "1999.98",
        "created_at": "2026-07-28T12:00:00+05:00"
    }
}
```

**Response `400`:**
```json
{
    "success": false,
    "errors": {
        "non_field_errors": ["You already have another product in cart. Remove it first."]
    }
}
```

---

#### `PATCH /api/cart/update/`

**Auth:** Bearer token

Increase or decrease cart quantity (min 1, max stock).

**Request:**
```json
{
    "action": "increase"
}
```

`action` is `"increase"` or `"decrease"`.

**Response `200`:**
```json
{
    "message": "Cart Updated successfully.",
    "data": {
        "id": 1,
        "product": 1,
        "quantity": 3,
        "product_name": "Galaxy S25",
        "product_price": "999.99",
        "total_price": "2999.97",
        "created_at": "2026-07-28T12:00:00+05:00"
    }
}
```

**Response `400`:**
```json
{
    "non_field_errors": ["Not enough stock."]
}
```

---

#### `DELETE /api/cart/remove/`

**Auth:** Bearer token

Clear the entire cart.

**Response `200`:**
```json
{
    "message": "Cart removed successfully!"
}
```

---

#### `POST /api/cart/order/`

**Auth:** Bearer token

**Deprecated** — use the PayPal flow (`/api/payments/`) for new checkouts.

Creates an order directly from the cart with the given saved address (snapshots address fields, reduces stock, clears cart).

**Request:**
```json
{
    "address_id": 1
}
```

**Response `201`:**
```json
{
    "success": true,
    "message": "Order created successfully.",
    "data": {
        "order_id": "ORD-3A8F2C1B",
        "total_price": "1999.98"
    }
}
```

---

#### `GET /api/cart/orders/`

**Auth:** Bearer token

List the authenticated user's order history, newest first (paginated).

**Response `200`:**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "order_id": "ORD-3A8F2C1B",
            "quantity": 2,
            "total_price": "1999.98",
            "product_name": "Galaxy S25",
            "product_price": "999.99",
            "full_name": "John Doe",
            "phone": "+1234567890",
            "address_line": "123 Main St",
            "city": "Karachi",
            "postal_code": "74000",
            "country": "Pakistan",
            "status": "processing",
            "payment_status": "paid",
            "created_at": "2026-07-28T12:00:00+05:00"
        }
    ]
}
```

Note: orders list is **not** wrapped in the standard envelope — it returns DRF's paginated list directly.

---

### Wishlist — `/api/wishlist/`

---

#### `GET /api/wishlist/`

**Auth:** Bearer token

List wishlist items.

**Response `200`:**
```json
[
    {
        "id": 1,
        "product": 1,
        "created_at": "2026-07-28T12:00:00+05:00"
    }
]
```

Note: not wrapped in the standard envelope.

---

#### `POST /api/wishlist/add/`

**Auth:** Bearer token

Add a product to the wishlist.

**Request:**
```json
{
    "product": 1
}
```

**Response `201`:**
```json
{
    "message": "Added to wishlist"
}
```

**Response `200`** (already in wishlist):
```json
{
    "message": "Already in wishlist"
}
```

**Response `404`** (product not found):
```json
{
    "error": "Product not found"
}
```

---

#### `DELETE /api/wishlist/remove/<int:wishlist_id>/`

**Auth:** Bearer token

Remove a wishlist item by its wishlist ID.

**Response `200`:**
```json
{
    "message": "Removed from wishlist"
}
```

**Response `404`:**
```json
{
    "error": "Item not found"
}
```

---

### Addresses — `/api/addresses/`

---

#### `GET /api/addresses/`

**Auth:** Bearer token

List saved addresses for the authenticated user.

**Response `200`:**
```json
[
    {
        "id": 1,
        "user": 1,
        "full_name": "John Doe",
        "phone": "+1234567890",
        "address_line": "123 Main St",
        "city": "Karachi",
        "postal_code": "74000",
        "country": "Pakistan",
        "is_default": true,
        "created_at": "2026-07-28T12:00:00+05:00"
    }
]
```

Note: not wrapped in the standard envelope.

---

#### `POST /api/addresses/`

**Auth:** Bearer token

Create a new address. If `is_default` is `true`, all other addresses for this user are unset as default.

**Request:**
```json
{
    "full_name": "John Doe",
    "phone": "+1234567890",
    "address_line": "123 Main St",
    "city": "Karachi",
    "postal_code": "74000",
    "country": "Pakistan",
    "is_default": true
}
```

**Response `201`:**
```json
{
    "id": 2,
    "user": 1,
    "full_name": "John Doe",
    "phone": "+1234567890",
    "address_line": "123 Main St",
    "city": "Karachi",
    "postal_code": "74000",
    "country": "Pakistan",
    "is_default": true,
    "created_at": "2026-07-28T12:05:00+05:00"
}
```

---

#### `DELETE /api/addresses/delete/<int:pk>/`

**Auth:** Bearer token

Delete a saved address.

**Response `200`:**
```json
{
    "message": "Deleted successfully"
}
```

**Response `404`:**
```json
{
    "error": "Address not found"
}
```

---

#### `POST /api/addresses/set-default/<int:pk>/`

**Auth:** Bearer token

Set an address as the default. Unsets any existing default.

**Response `200`:**
```json
{
    "message": "Default address set"
}
```

**Response `404`:**
```json
{
    "error": "Address not found"
}
```

---

### Payments (PayPal) — `/api/payments/`

---

#### `POST /api/payments/create-order/`

**Auth:** Bearer token

Create a PayPal order from the current cart. Returns the PayPal order ID and an approval URL to redirect the customer to PayPal.

**Request:**
```json
{
    "address_id": 1
}
```

**Response `201`:**
```json
{
    "success": true,
    "message": "PayPal order created successfully.",
    "data": {
        "paypal_order_id": "6ST12345ABC67890",
        "status": "CREATED",
        "approval_url": "https://www.sandbox.paypal.com/checkoutnow?token=6ST12345ABC67890",
        "amount": "1999.98",
        "currency": "USD"
    }
}
```

**Response `400`:**
```json
{
    "success": false,
    "message": "Cart is empty.",
    "errors": {
        "validation": "Cart is empty."
    }
}
```

---

#### `POST /api/payments/capture-order/`

**Auth:** Bearer token

Capture an approved PayPal order. On success, creates an `Order` and `Payment` record, reduces stock, clears the cart, and queues a confirmation email. Idempotent — calling with the same PayPal order ID returns the existing result.

**Request:**
```json
{
    "paypal_order_id": "6ST12345ABC67890",
    "address_id": 1
}
```

**Response `201`:**
```json
{
    "success": true,
    "message": "Payment captured successfully.",
    "data": {
        "order_id": "ORD-3A8F2C1B",
        "paypal_order_id": "6ST12345ABC67890",
        "paypal_capture_id": "8YT12345ABC67890",
        "status": "processing",
        "order_status": "processing",
        "payment_status": "paid",
        "amount": "1999.98"
    }
}
```

**Response `400`:**
```json
{
    "success": false,
    "message": "Payment was not completed.",
    "errors": {
        "validation": "Payment was not completed."
    }
}
```

---

### Models

| Model | Purpose |
|---|---|
| `User` | Email-based account; inactive until email verification. No username field — `email` is `USERNAME_FIELD`. |
| `Brand`, `Category`, `Mobile` | Catalogue structure and mobile inventory. |
| `Specification`, `MobileSpecification`, `MobileImage` | Product attributes and Cloudinary-hosted images. |
| `Review` | One review per user per product (only purchasable products). |
| `Cart` | `OneToOneField` to `User` — one product entry per user, adjustable quantity. |
| `Address` | User-owned delivery addresses; `is_default` flag. |
| `Order` | Ordered product details, price & address snapshots, fulfilment and payment status. |
| `Payment` | `OneToOneField` to `Order` — PayPal transaction details. |
| `Wishlist` | User-saved products. |

### PayPal checkout flow

1. Add a product to the cart and create a saved address.
2. Call `POST /api/payments/create-order/` with the address ID. Redirect the customer to `approval_url`.
3. Customer approves payment on PayPal.
4. Call `POST /api/payments/capture-order/` with the PayPal order ID and address ID.

On successful capture, the API:
- Verifies the PayPal-completed amount matches the cart total
- Creates an `Order` (status: `processing`, payment: `paid`)
- Creates a `Payment` record linked to the order
- Reduces product stock
- Clears the cart
- Queues an async confirmation email via Celery
- A repeated capture for the same PayPal order returns the existing result (idempotent)

### Development notes

- `is_active=False` on user creation — email verification required before login.
- Password hasher: `accounts.hashers.FastPBK2PasswordHasher` (100k PBKDF2 iterations).
- `Order` snapshots address fields as string copies (not FK to `Address`).
- CORS permits `http://localhost:5173` by default (Vite dev server).
- `TIME_ZONE = 'Asia/Karachi'`.
- Changing an order's status in Django admin queues a customer notification email via Celery (after transaction commit).
- Keep `.env` out of version control. Use PayPal sandbox credentials for local testing; switch `PAYPAL_MODE=production` only for deployment.

---

# Part 2 — Admin App (`/api/admin/`)

The admin app is a superuser-only API for store management. It provides JWT auth via HttpOnly cookies, dashboard analytics, and an AI-powered chat agent.

## Authentication

Unlike the customer API, the admin API does **not** use the `Authorization: Bearer` header. Tokens are stored in signed, HttpOnly cookies:

| Cookie | Purpose | Lifetime |
|---|---|---|
| `admin_access_token` | Access token | 15 minutes |
| `admin_refresh_token` | Refresh token | 7 days |

- Both cookies are `HttpOnly`, `Secure`, `SameSite=None`, and path-scoped to `/api/admin/`.
- Only `auth/login/` and `auth/refresh/` are public. All other endpoints require superuser privileges (`IsSuperUser`).
- **Logout** blacklists the refresh token and clears both cookies.

## Endpoints

### Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/admin/auth/login/` | Public | Login with `{email, password}`. Superuser only. Sets auth cookies. |
| `POST` | `/api/admin/auth/logout/` | Superuser | Blacklists the refresh token and clears auth cookies. |
| `POST` | `/api/admin/auth/refresh/` | Public | Rotates access + refresh cookies from the refresh cookie. |
| `GET` | `/api/admin/auth/me/` | Superuser | Returns `{email, first_name, last_name}` of the current admin. |

### Dashboard

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/admin/dashboard/summary/?days=<N>` | Superuser | Store analytics summary. `days` is clamped to 1–90 (default 15). |

Returns `summary` (`total_orders`, `orders_by_status`, `total_revenue`, `new_users`) and a `daily` breakdown for each day in the range.

### Chat (AI agent)

The chat agent (LangChain + Mistral) answers store questions and can invoke tools.

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/admin/chat/` | Superuser | Non-streaming reply. Body: `{message, conversation?}`. Returns `{conversation, message}`. |
| `POST` | `/api/admin/chat/stream/` | Superuser | Streaming reply over Server-Sent Events (SSE), `text/event-stream`. |

**Chat request body:**

| Field | Type | Description |
|---|---|---|
| `message` | string | User input (max 5000 chars, non-empty). |
| `conversation` | int | Optional existing conversation ID; omitted for a new chat. |

**SSE events** (each event carries a JSON payload):

| Event | Payload |
|---|---|
| `message.started` | `{conversation}` |
| `content.delta` | `{delta}` — streamed text tokens |
| `tool.call` | `{id, name, input}` — tool invocation started |
| `tool.result` | `{id, name, output}` — tool invocation result |
| `message.completed` | `{conversation, message}` — final persisted reply |
| `error` | `{code, message}` |

### Conversations

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/admin/conversations/` | Superuser | List the admin's conversations (newest first). |
| `DELETE` | `/api/admin/conversations/<id>/` | Superuser | Delete a conversation (`204 No Content`). |
| `GET` | `/api/admin/conversations/<id>/messages/` | Superuser | List messages of a conversation in chronological order. |

Each conversation has `{id, title, created_at, updated_at}`; each message has `{id, role, content, created_at}` where `role` is `user` or `assistant`.

## Admin chat model

| Model | Purpose |
|---|---|
| `Conversation` | A chat thread owned by a superuser; auto-titled from the first user message. |
| `Message` | A single `user` or `assistant` message within a conversation. |

## Mistral configuration

The chat agent requires a Mistral API key (see setup guide). It reads `MISTRAL_API_KEY`, `MISTRAL_MODEL`, and `MISTRAL_TEMPERATURE` from the environment.
