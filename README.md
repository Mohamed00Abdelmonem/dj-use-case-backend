# Use Case Hub — Django REST API Backend

A production-oriented Django REST API backend built for the **Use Case Hub** application. It provides domain management, hierarchical portfolio loading, system gap tracking, integration management, developer assignment, and real-time server-side analytics.

---

## 🏗️ Architecture & App Structure

The backend is built around clean business domain boundaries using modular Django apps:

```text
src/
├── manage.py
├── pytest.ini
├── project/
│   ├── settings.py       # Configuration, CORS, DRF, & installed apps
│   ├── urls.py           # Root REST router & API routing
│   └── wsgi.py
├── apps/
│   ├── portfolio/        # Domain, Category, & UseCase models, ViewSets, & Tree endpoints
│   ├── gaps/             # GapClassification & Gap models, ViewSets, & search/filters
│   ├── integrations/     # System Integration model, ViewSet, & search/filters
│   ├── people/           # Developer / Owner model, ViewSet, & search/filters
│   ├── core/             # Settings endpoint & seed_data management command
│   └── analytics/        # Server-side aggregations & AnalyticsView
└── tests/                # Unit & integration test suites
```

---

## 🚀 Technologies Used

- **Python 3.11+ / 3.14**
- **Django 5.2**
- **Django REST Framework (DRF) 3.18**
- **django-cors-headers** (CORS support for React frontend)
- **django-filter** (Server-side search & filter backend)
- **pytest & pytest-django** (Automated testing framework)

---

## 🛠️ Quick Start Guide

### 1. Prerequisites & Virtual Environment

Create and activate a virtual environment:

```bash
python -m venv venv

# On Windows (PowerShell)
.\venv\Scripts\activate

# On Linux/macOS
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Migrations

Apply database migrations:

```bash
python manage.py migrate
```

### 4. Seed Initial Data

Populate the database with the initial Use Case Hub catalogue dataset:

```bash
python manage.py seed_data
```

### 5. Run Development Server

Start the Django development server on port 8000:

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`.

---

## 📡 REST API Reference

| Endpoint | Method | Description | Search / Filters |
| :--- | :--- | :--- | :--- |
| `/api/portfolio/` | `GET` | Full hierarchical portfolio tree (Domains → Categories → Use Cases) | — |
| `/api/portfolio/import/` | `POST` | Atomic transactional bulk import of portfolio JSON | — |
| `/api/settings/` | `GET` | Choice configurations (allowed statuses, priorities, catalogue width) | — |
| `/api/analytics/` | `GET` | Aggregated analytics (KPI cards & chart distributions) | — |
| `/api/domains/` | `GET`, `POST`, `PATCH`, `DELETE` | Domain CRUD operations | `search` |
| `/api/categories/` | `GET`, `POST`, `PATCH`, `DELETE` | Category CRUD operations | `domain`, `search` |
| `/api/use-cases/` | `GET`, `POST`, `PATCH`, `DELETE` | Use Case CRUD operations | `status`, `category`, `search` |
| `/api/developers/` | `GET`, `POST`, `PATCH`, `DELETE` | Developer / Owner CRUD operations | `search` |
| `/api/gap-classifications/` | `GET`, `POST`, `PATCH`, `DELETE` | Gap Classification CRUD operations | `search` |
| `/api/gaps/` | `GET`, `POST`, `PATCH`, `DELETE` | System Gap CRUD operations | `status`, `priority`, `classification`, `search` |
| `/api/integrations/` | `GET`, `POST`, `PATCH`, `DELETE` | System Integration CRUD operations | `status`, `type`, `direction`, `search` |

---

## 🧪 Running Tests

Run the test suite using Django's test runner or `pytest`:

```bash
# Django test runner
python manage.py test

# Pytest
pytest
```

---

## 🔒 Data Protection Rules

- **Protected Domain Deletion**: Domains containing categories cannot be deleted directly (returns HTTP 400 with a detailed error message).
- **Protected Category Deletion**: Categories containing use cases cannot be deleted directly (returns HTTP 400).
- **Transactional Bulk Import**: `/api/portfolio/import/` runs inside an `@transaction.atomic` block to guarantee partial imports never corrupt database state.

---

## 🔗 React Frontend Integration

To connect the React frontend (`use-case-hub-frontend`):

Set `.env` in the frontend root:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_USE_MOCK_DATA=false
```

---

## 🐳 Production Deployment Guide (Docker & Docker Compose)

This backend is packaged with Gunicorn, PostgreSQL, and Docker Compose for production deployment on Ubuntu 24.04 (or any Docker-capable server).

### 1. Environment Setup

Copy `.env.example` to create your production environment configuration:

```bash
cp .env.example .env
```

Edit `.env` to configure production secrets:

```env
SECRET_KEY=your-secure-randomly-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=api.yourdomain.com,your-server-ip,localhost

DB_ENGINE=django.db.backends.postgresql
DB_NAME=use_case_hub
DB_USER=postgres
DB_PASSWORD=your-strong-db-password
DB_HOST=db
DB_PORT=5432

CORS_ALLOWED_ORIGINS=https://yourdomain.com,http://localhost:3000
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

### 2. Build and Launch Containers

Build and start the PostgreSQL and Django backend containers in detached mode:

```bash
docker compose up -d --build
```

The container entrypoint script will automatically:
1. Wait for PostgreSQL to become ready.
2. Execute all pending database migrations (`python manage.py migrate --noinput`).
3. Collect static files into `STATIC_ROOT` (`python manage.py collectstatic --noinput`).
4. Launch Gunicorn WSGI server on port `8000` with 3 worker processes.

### 3. Verification & Log Inspection

Check container status:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f backend
```

Check database logs:

```bash
docker compose logs -f db
```

### 4. Running Administrative Commands in Production

Seed initial data (optional):

```bash
docker compose exec backend python manage.py seed_data
```

Create a superuser:

```bash
docker compose exec backend python manage.py createsuperuser
```

Run test suite inside container:

```bash
docker compose exec backend python manage.py test
```

### 5. Stopping and Restarting Services

Restart services:

```bash
docker compose restart
```

Stop containers (preserving database volume):

```bash
docker compose down
```

### 6. Updating the Application

When pulling new code:

```bash
git pull origin main
docker compose up -d --build
```

