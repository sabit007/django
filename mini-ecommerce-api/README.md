# Mini E-commerce REST API

A small e-commerce backend built with **Django REST Framework**, covering
CRUD APIs, serializers, model relationships, token authentication,
filtering/searching/ordering, and pagination.

## Features

- **Category API** — full CRUD.
- **Product API** — full CRUD, with `name`, `description`, `price`, `stock`,
  `category`, `created_date`.
- **Search / Filter / Order / Paginate** on products.
- **Token Authentication** — log in to get a token, then use it to access
  protected endpoints.
- **Order API** — authenticated users can place orders and view only their
  own order history.
- **Bonus**: stock validation (an order can't exceed available stock, and
  stock is decremented automatically), `total_price` is always
  server-computed from `product.price * quantity` (never trusted from the
  client).

## Project Structure

```
mini-ecommerce-api/
├── ecommerce_api/        # Django project (settings, urls, wsgi/asgi)
├── shop/                 # Main app: models, serializers, views, urls
│   ├── models.py         # Category, Product, Order
│   ├── serializers.py
│   ├── views.py          # ModelViewSets
│   ├── filters.py        # django-filter FilterSet for Product
│   ├── urls.py           # DRF router
│   ├── admin.py
│   └── tests.py
├── manage.py
├── requirements.txt
└── README.md
```

## Setup

```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd mini-ecommerce-api

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create an admin/test user
python manage.py createsuperuser

# 6. Run the server
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000/api/`.

## Authentication

Token auth is used. Obtain a token by posting your credentials:

```
POST /api/login/
{
    "username": "your_username",
    "password": "your_password"
}
```

Response:

```json
{ "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" }
```

Then include it on every protected request:

```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

Categories and products can be **listed/viewed by anyone**; creating,
updating, or deleting them requires a valid token. All order endpoints
require a valid token.

## Endpoints

### Categories

| Method | URL                      | Description        |
|--------|--------------------------|---------------------|
| GET    | `/api/categories/`       | List all categories |
| POST   | `/api/categories/`       | Create a category   |
| GET    | `/api/categories/{id}/`  | Retrieve a category |
| PUT    | `/api/categories/{id}/`  | Update a category   |
| PATCH  | `/api/categories/{id}/`  | Partial update      |
| DELETE | `/api/categories/{id}/`  | Delete a category   |

### Products

| Method | URL                    | Description        |
|--------|------------------------|---------------------|
| GET    | `/api/products/`       | List products       |
| POST   | `/api/products/`       | Add a product       |
| GET    | `/api/products/{id}/`  | Product details     |
| PUT    | `/api/products/{id}/`  | Update a product    |
| PATCH  | `/api/products/{id}/`  | Partial update      |
| DELETE | `/api/products/{id}/`  | Delete a product    |

**Search / filter / order / paginate:**

```
GET /api/products/?search=phone
GET /api/products/?category=1
GET /api/products/?price=499.99
GET /api/products/?price_min=100&price_max=1000
GET /api/products/?ordering=price
GET /api/products/?ordering=-price
GET /api/products/?page=2
```

### Orders (requires authentication)

| Method | URL                  | Description                    |
|--------|----------------------|----------------------------------|
| GET    | `/api/orders/`       | List the logged-in user's orders |
| POST   | `/api/orders/`       | Create an order                  |
| GET    | `/api/orders/{id}/`  | View a single order (own only)   |

Creating an order only requires `product` and `quantity`; `total_price`,
`user`, and `order_date` are set automatically:

```json
POST /api/orders/
{
    "product": 1,
    "quantity": 2
}
```

## Testing

Run the test suite:

```bash
python manage.py test
```

A `tests.py` file covers category permissions, product search/filter/
ordering, order creation (total price + stock decrement), stock validation,
and per-user order visibility.

For manual testing, import the endpoints above into **Postman** (or use the
DRF browsable API at `/api/products/`, `/api/categories/`, `/api/orders/`
in your browser once logged in via `/admin/` or a token).

## Notes on Design Decisions

- SQLite is used for simplicity; swap the `DATABASES` setting in
  `ecommerce_api/settings.py` for Postgres/MySQL in production.
- `Order.total_price` is calculated server-side in `Order.save()` and in the
  serializer's `create()` — it can never be spoofed by a client.
- Stock is decremented when an order is created, and an order requesting
  more than the available stock is rejected with a `400` response.
