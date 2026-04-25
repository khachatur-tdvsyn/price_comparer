# Price Comparer

A Django-based web application for comparing product prices across multiple e-commerce platforms. This tool scrapes product data, handles currency conversions, and provides a REST API for price analysis and comparison.

## Features

- **Currency Management**: Automatic currency exchange rate tracking and conversion
- **Price History**: Records historical price data for trend analysis
- **Fee Calculation**: Tracks various fees including shipping, taxes, and import duties
- **REST API**: Full RESTful API built with Django REST Framework
- **Background Tasks**: Asynchronous scraping using Celery
- **Admin Interface**: Django admin panel for data management
- **API Documentation**: Auto-generated OpenAPI documentation with drf-spectacular

## Tech Stack

- **Backend**: Django 6.0+
- **API**: Django REST Framework
- **Task Queue**: Celery
- **Database**: SQLite (development) / PostgreSQL (production recommended)
- **Documentation**: drf-spectacular (OpenAPI/Swagger)
- **Web Scraping**: Custom scrapers with Selenium support

## Installation

### Prerequisites

- Python 3.8+
- pip
- Virtualenv (recommended)

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd price_comparer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install django djangorestframework drf-spectacular celery nanoid
   ```
   Note: Add other dependencies as needed (e.g., selenium for scraping).

4. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

5. Load initial currency data:
   ```bash
   python manage.py load_currencies
   ```

6. Create a superuser for admin access:
   ```bash
   python manage.py createsuperuser
   ```

## Usage

### Running the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### Running Celery Worker

For background scraping tasks:

```bash
celery -A price_comparer worker --loglevel=info
```

### Running Celery Beat

For scheduled tasks (e.g., currency rate updates):

```bash
celery -A price_comparer beat --loglevel=info
```

### API Endpoints

- `GET /api/sellers/` - List sellers
- `GET /api/tags/` - List product tags
- `GET /api/items/` - List products with price comparison
- `GET /api/items/{id}/history/` - Price history for a specific item
- `GET /api/currencies/` - Currency information

### API Documentation

View the interactive API documentation at:
- Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`

### Admin Panel

Access the Django admin at `http://localhost:8000/admin/` using the superuser credentials.

## Project Structure

```
price_comparer/
├── main/                 # Main app with models and API
│   ├── models.py         # Database models (Item, Currency, Fee, etc.)
│   ├── views.py          # REST API viewsets
│   ├── serializers.py    # DRF serializers
│   └── urls.py           # URL routing
├── scrape/               # Scraping functionality
│   ├── tasks.py          # Celery tasks for scraping
│   └── scraper/          # Scraper implementations
│       ├── base.py       # Base scraper class
│       ├── ebay.py       # eBay scraper
│       └── currency.py   # Currency rate scraper
├── price_comparer/       # Django project settings
│   ├── settings.py       # Main settings
│   ├── urls.py           # Root URL configuration
│   └── celery.py         # Celery configuration
└── tmp/                  # Temporary files and guides
```

## Models

- **Item**: Product information with source, seller, and tags
- **RecordedData**: Price history and ratings
- **Fee**: Various fees associated with items
- **Currency**: Currency codes with exchange rates
- **Seller**: Seller information per platform
- **Tag**: Product categorization tags

## Scraping

The application includes scrapers for:
- eBay product listings
- Currency exchange rates
- Other platforms (Amazon, AliExpress, WildBerries - extensible)

Scraping tasks are run asynchronously via Celery.

## License

This project is provided for educational purposes.