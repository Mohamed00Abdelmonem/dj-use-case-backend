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
pip install Django djangorestframework django-cors-headers django-filter pytest pytest-django
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
