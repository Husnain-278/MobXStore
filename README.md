# MobXStore — Mobile E‑Commerce API

## Overview
- Mobile‑first e‑commerce backend built with Django 6 + DRF, PostgreSQL, and uv.
- Email‑verified JWT authentication (register → verify → login → token).
- Full product catalogue: brands, categories, mobiles with filtering, search, pagination.
- Shopping features: cart (single product per user), wishlist, addresses, order history.
- PayPal checkout (sandbox/production) with idempotent capture flow.
- Async email delivery via Celery + Brevo, Cloudinary image hosting.
- Admin API (`/api/admin/`) for superusers: analytics, chat AI (Mistral), management tools.

## Download & Setup Guide
1. **Clone** the repository and `cd` into it.  
   ```bash
   git clone <repo-url> && cd MobXStore
   ```
2. **Copy environment template** and fill in your credentials.  
   ```bash
   cp .env.example .env
   ```
   Edit `.env` – all variables are documented (DB, JWT, Cloudinary, PayPal, Brevo, Mistral, etc.).
3. **Install dependencies**  
   ```bash
   uv sync
   ```
4. **Apply migrations**  
   ```bash
   uv run python manage.py migrate
   ```
5. **(Optional) Create a superuser** to access the admin API.  
   ```bash
   uv run python manage.py createsuperuser
   ```
6. **Seed sample data** (optional, loads product images to Cloudinary).  
   ```bash
   uv run python manage.py generate_fake_products --count 12 --category-count 6
   ```
7. **Start the development server**  
   ```bash
   uv run python manage.py runserver
   ```
   API is reachable at `http://localhost:8000/api/`.  
   Admin API at `http://localhost:8000/api/admin/`.
8. **Start Redis & Celery** (required for email sending).  
   ```bash
   redis-server &
   uv run celery -A store_backend worker -l info
   ```

## API Reference

| Endpoint | Method | Request Body | Response |
|----------|--------|--------------|----------|
| `/api/accounts/register/` | POST | `{ "email": "...", "password": "..." }` | `{ "success": true, "message": "Account created. Please check your email to verify your account.", "data": null, "errors": null }` (or 400 with `errors`) |
| `/api/accounts/verify-email/<uidb64>/<token>/` | GET | – | `{ "success": true, "message": "Email verified Successfully!", "data": null, "errors": null }` (400 on error) |
| `/api/accounts/login/` | POST | `{ "email": "...", "password": "..." }` | `{ "access": "...", "refresh": "..." }` (unwrapped) |
| `/api/products/brands/` | GET | – | `{ "count": N, "next": "...", "previous": "...", "results": { "success": true, "message": "...", "data": [{id, name, logo, slug}, …], "errors": null } }` |
| `/api/products/categories/` | GET | – | Same envelope as brands |
| `/api/products/mobiles/` | GET | Query params: `brand`, `category`, `min_price`, `max_price`, `search`, `ordering`, `page`, `page_size` | Same envelope, `results.data` contains mobile objects with `price`, `stock`, `primary_image`, etc. |
| `/api/products/mobiles/<slug:slug>/` | GET | – | `{ "success": true, "message": "Mobile Detail fetched", "data": { "id": ..., "name": "...", "brand": "...", "price": "...", "description": "...", "primary_image": "...", "brand": "...", "category": "...", "images": [{ "id": ..., "image": "..." }, ...], "specifications": [{ "name": "...", "value": "..." }, ...], "created_at": "...", "average_rating": ..., "total_reviews": ..., "reviews": [{ "id": ..., "user": "...", "rating": ..., "comment": "...", "created_at": "..." }], "errors": null } }` |
| `/api/products/add-review/` | POST | `{ "product_id": 1, "rating": 5, "comment": "..." }` | `{ "success": true, "message": "Review added successfully", "data": { "id": 1, "product": 1, "rating": 5, "comment": "...", "created_at": "..." }, "errors": null }` (400 on duplicate) |
| `/api/cart/` | GET | – (auth) | `{ "success": true, "message": null, "data": { "id": 1, "product": 1, "quantity": 2, "product_name": "...", "product_price": "...", "total_price": "...", "created_at": "..." }, "errors": null }` (404 if empty) |
| `/api/cart/add-to-cart/` | POST | `{ "product_id": 1, "quantity": 1 }` | `{ "success": true, "data": { "id": 1, "product": 1, "quantity": 2, "product_name": "...", "product_price": "...", "total_price": "...", "created_at": "..." }, "errors": null }` (400 if cart already has another product) |
| `/api/cart/update/` | PATCH | `{ "action": "increase" or "decrease" }` | `{ "message": "Cart Updated successfully.", "data": { "id": 1, "quantity": 3, ... }, "errors": null }` (400 on insufficient stock) |
| `/api/cart/remove/` | DELETE | – | `{ "message": "Cart removed successfully!" }` |
| `/api/cart/orders/` | GET | – | Raw DRF paginated list of orders (no envelope) – each item contains `order_id`, `quantity`, `total_price`, address fields, `status`, `payment_status`, `created_at`, etc. |
| `/api/wishlist/` | GET | – | `[ { "id": 1, "product": 1, "created_at": "..." }, … ]` (not wrapped) |
| `/api/wishlist/add/` | POST | `{ "product": 1 }` | `{ "message": "Added to wishlist" }` (201) / `{ "message": "Already in wishlist" }` (200) |
| `/api/wishlist/remove/<int:wishlist_id>/` | DELETE | – | `{ "message": "Removed from wishlist" }` |
| `/api/addresses/` | GET | – | `[ { "id": 1, "full_name": "...", "phone": "...", "address_line": "...", "city": "...", "postal_code": "...", "country": "...", "is_default": true, "created_at": "..." }, … ]` |
| `/api/addresses/` | POST | `{ "full_name": "...", "phone": "...", "address_line": "...", "city": "...", "postal_code": "...", "country": "...", "is_default": true }` | Created object with `id`, `created_at`, etc. |
| `/api/addresses/delete/<int:pk>/` | DELETE | – | `{ "message": "Deleted successfully" }` |
| `/api/addresses/set-default/<int:pk>/` | POST | – | `{ "message": "Default address set" }` |
| `/api/payments/create-order/` | POST | `{ "address_id": 1 }` | `{ "success": true, "message": "PayPal order created successfully.", "data": { "paypal_order_id": "...", "status": "CREATED", "approval_url": "...", "amount": "...", "currency": "USD" } }` |
| `/api/payments/capture-order/` | POST | `{ "paypal_order_id": "...", "address_id": 1 }` | `{ "success": true, "message": "Payment captured successfully.", "data": { "order_id": "ORD-...", "paypal_order_id": "...", "paypal_capture_id": "...", "status": "processing", "payment_status": "paid", "amount": "..." } }` |
| `/api/admin/auth/login/` | POST | `{ "email": "...", "password": "..." }` | Sets `admin_access_token` & `admin_refresh_token` cookies |
| `/api/admin/auth/logout/` | POST | – | Clears auth cookies |
| `/api/admin/auth/refresh/` | POST | – | Refreshes access & refresh cookies |
| `/api/admin/auth/me/` | GET | – | Returns `{ "email": "...", "first_name": "...", "last_name": "..." }` |
| `/api/admin/dashboard/summary/` | GET | `?days=N` | `{ "summary": { "total_orders": N, ... }, "daily": [ {...}, … ] }` |
| `/api/admin/chat/` | POST | `{ "message": "...", "conversation": 123? }` | `{ "conversation": 123, "message": "Answer..." }` |
| `/api/admin/chat/stream/` | POST | Same as above | SSE stream with `message.started`, `content.delta`, `tool.call`, `tool.result`, `message.completed`, `error` events |
| `/api/admin/conversations/` | GET | – | List of conversations (newest first) |
| `/api/admin/conversations/<id>/` | DELETE | – | Deletes conversation (204) |
| `/api/admin/conversations/<id>/messages/` | GET | – | List of messages in that conversation |

*All successful responses follow the standard envelope*: `{ "success": true, "message": "...", "data": ..., "errors": null }`  
*Error responses*: `{ "success": false, "message": "...", "data": null, "errors": { ... } }` (or raw DRF errors for some endpoints).

## Development notes (summary)
- Users are created inactive (`is_active=False`) and must verify email before login.  
- Passwords hashed with `FastPBK2PasswordHasher` (100 k iterations).  
- `Order` stores snapshots of address fields; no FK to `Address`.  
- CORS permits `http://localhost:5173`.  
- Time zone: `Asia/Karachi`.  
- Keep `.env` out of version control; use PayPal sandbox for local testing.  
- Admin chat requires `MISTRAL_API_KEY`, `MISTRAL_MODEL`, `MISTRAL_TEMPERATURE` env vars.