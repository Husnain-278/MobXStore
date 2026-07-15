# MobXStore — E-Commerce Backend

A Django REST Framework backend for a mobile e-commerce store. Supports JWT auth, product browsing, cart, wishlist, addresses, and order management.

## Tech Stack

- **Django 6.0.3** + **Django REST Framework**
- **JWT Auth** (`djangorestframework-simplejwt`)
- **PostgreSQL** (via env variables)
- **Cloudinary** (image hosting)
- **Celery** + **Redis** (async email tasks)
- **Brevo (Sendinblue)** (email delivery)

---

## API Endpoints

### Accounts — `api/accounts/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/accounts/register/` | Public | Create account. Sends verification email. Body: `{ "email", "password" }` |
| POST | `/api/accounts/login/` | Public | Login. Returns JWT tokens. Body: `{ "email", "password" }` |
| GET | `/api/accounts/verify-email/<uidb64>/<token>/` | Public | Verify email address via link |
| GET | `/api/accounts/profile/` | JWT | Get authenticated user's profile |

### Products — `api/products/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/products/brands/` | Public | List all brands (paginated) |
| GET | `/api/products/categories/` | Public | List all categories (paginated) |
| GET | `/api/products/mobiles/` | Public | List mobiles with filtering & pagination |
| GET | `/api/products/mobiles/<slug>/` | Public | Get mobile detail (specs, images, reviews, avg rating) |
| POST | `/api/products/add-review/` | JWT | Add review (must have purchased). Body: `{ "product_id", "rating", "comment?" }` |

**Filters for `GET /api/products/mobiles/`:**

| Param | Description |
|-------|-------------|
| `brand` | Filter by brand slug |
| `category` | Filter by category slug |
| `min_price` / `max_price` | Price range |
| `search` | Search mobile name |
| `ordering` | Sort by `price` (prefix with `-` for descending) |

### Cart — `api/cart/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/cart/` | JWT | Get current cart |
| POST | `/api/cart/add-to-cart/` | JWT | Add product to cart. Body: `{ "product_id", "quantity?" }` |
| PATCH | `/api/cart/update/` | JWT | Increase/decrease quantity. Body: `{ "action": "increase" | "decrease" }` |
| DELETE | `/api/cart/remove/` | JWT | Clear entire cart |
| POST | `/api/cart/order/` | JWT | Place order from cart. Body: `{ "payment_method", "address_id" }` |
| GET | `/api/cart/orders/` | JWT | List order history (paginated, newest first) |

### Wishlist — `api/wishlist/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/wishlist/` | JWT | List wishlist items |
| POST | `/api/wishlist/add/` | JWT | Add product. Body: `{ "product": <id> }` |
| DELETE | `/api/wishlist/remove/<wishlist_id>/` | JWT | Remove item by wishlist ID |

### Addresses — `api/addresses/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/addresses/` | JWT | List saved addresses |
| POST | `/api/addresses/` | JWT | Create address |
| DELETE | `/api/addresses/delete/<pk>/` | JWT | Delete address |
| POST | `/api/addresses/set-default/<pk>/` | JWT | Set address as default |

---

## Auth Flow

1. **Register** at `/api/accounts/register/` → account created with `is_active=False`
2. Click verification link from email → `/api/accounts/verify-email/<uidb64>/<token>/`
3. **Login** at `/api/accounts/login/` → receive `access` and `refresh` JWT tokens
4. Include `Authorization: Bearer <access_token>` header in all authenticated requests

---

## Models Overview

| Model | Key Fields |
|-------|------------|
| `User` | `email` (unique, login field), `password`, `is_active` (default False) |
| `Brand` | `name`, `slug`, `logo` (Cloudinary) |
| `Category` | `name`, `slug` |
| `Mobile` | `name`, `brand`, `category`, `price`, `stock`, `description`, `primary_image` |
| `Specification` | `name` |
| `MobileSpecification` | `mobile`, `specification`, `value` |
| `MobileImage` | `mobile`, `image` (Cloudinary), `is_primary` |
| `Review` | `user`, `product`, `rating` (1-5), `comment` |
| `Cart` | `user` (OneToOne), `product`, `quantity` |
| `Order` | `user`, `product`, `order_id`, `quantity`, `total_price`, `status`, `payment_method`, `payment_status`, address snapshot fields |
| `Address` | `user`, `full_name`, `phone`, `address_line`, `city`, `postal_code`, `country`, `is_default` |
| `Wishlist` | `user`, `product` |

---

## Setup

1. **Clone and create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables** (database URL, Cloudinary creds, Brevo API key, Redis URL)

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start development server**
   ```bash
   python manage.py runserver
   ```

6. **Start Celery worker** (for async emails)
   ```bash
   celery -A store_backend worker -l info
   ```
