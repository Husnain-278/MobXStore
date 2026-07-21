# MobXStore — Agent Guide

## Stack
- Python 3.12, Django 6.0.3, DRF 3.17+, PostgreSQL
- JWT (`djangorestframework-simplejwt`), `Bearer` auth header
- Celery + Redis (broker), Brevo/Sendinblue SDK for email
- Cloudinary for images, `django-cloudinary-storage`
- `uv` package manager (see `uv.lock`, `pyproject.toml`)

## Setup & commands
- Env: copy `.env.example` → `.env`, then `uv sync`
- Run: `uv run python manage.py runserver`
- Celery worker: `uv run celery -A store_backend worker -l info`
- Seed DB: `uv run python manage.py generate_fake_products --count 12 --category-count 6`
  (uploads images from `assets/` to Cloudinary)
- Migrate: `uv run python manage.py migrate`
- Tests: none exist yet (`pytest` not configured, test stubs are empty)

## Django apps (5)
| App | URL prefix | Purpose |
|-----|------------|---------|
| `accounts` | `api/accounts/` | Register/login/verify-email/profile |
| `products` | `api/products/` | Brands, categories, mobiles, reviews |
| `cart` | `api/cart/` | Cart CRUD, place order, order history |
| `wishlist` | `api/wishlist/` | Wishlist CRUD |
| `addresses` | `api/addresses/` | Address CRUD, set-default |

## Auth quirks
- Custom `User` model: `email` is `USERNAME_FIELD`, no `username` field
- `is_active=False` on creation; must verify email link to activate
- Only password hasher: `accounts.hashers.FastPBK2PasswordHasher` (100k PBKDF2 iterations — faster but less secure)
- Email verification: `accounts/tokens.py` — generates token, `accounts/tasks.py` sends via Celery

## Model quirks
- `Cart` is `OneToOneField` to `User` — one product entry per user cart
- `Order` snapshots address fields (string copies, not FK to `Address`)
- `Mobile.primary_image` is `CloudinaryField` (no upload to local disk)
- `Review` has `unique_together = ['user', 'product']` — one review per user per product

## API response pattern
All views return: `{ "success": bool, "message": str, "data": ..., "errors": ... }`

## Important settings (settings.py)
- `.env` loaded via `python-dotenv` at module level
- `CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]` (Vite dev server)
- `TIME_ZONE = 'Asia/Karachi'`
- Pagination: `PageNumberPagination`, page_size=10, max 100
- No CI, pre-commit, or type checker configured

## Celery
- Auto-discovers tasks via `@shared_task` in app `tasks.py`
- `send_verification_email` (accounts) and `send_order_confirmation_email` (cart)
- Workers need Redis running locally
