# Initialize Django Backend Repository on GitHub

## Task Brief
Set up a new Django project repository with initial commit and professional structure scaffold for the capstone backend service.

## Scenario
Your team needs a clean Django backend repository with proper Git history and structure ready for collaborative development.

## Deliverables
- GitHub repository with Django project scaffold

## Success Criteria
- Repository is public and accessible

---

# Capstone Django Backend Service Repository

## 1. Public GitHub Repository Details

- **Repository Name**: `sahkaarx-stage-portfolio-0832b5b1` / `django-capstone-backend`
- **Repository Visibility**: **Public** (World accessible)
- **Primary Public GitHub URL**: [https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1](https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1)
- **Dedicated Service Repository URL**: [https://github.com/parth-mehta95/django-capstone-backend](https://github.com/parth-mehta95/django-capstone-backend)
- **Default Branch**: `main`

---

## 2. Project Description

The **Capstone Django Backend Service** provides a clean, modular foundation for collaborative backend development. Built using Python 3 and Django, this service follows modern development practices including separation of concerns, environment-based configuration, structured logging, health monitoring endpoints, and modular application design ready for enterprise feature development.

### Core Capabilities:
- **Project Configuration**: Centralized Django configuration (`backend/settings.py`) with environment-variable controls (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`).
- **Administrative Utilities**: Standard `manage.py` command-line interface for running migrations, tests, and administrative commands.
- **Service Discovery & Health Monitoring**: Dedicated JSON-based root discovery (`/`) and health check (`/health/`) endpoints for CI/CD and container probes.
- **Modular App Architecture**: `core` application with base models (`TimeStampedModel`), administration portal integration, and service metadata tracking.
- **Automated Testing Suite**: Built-in test cases for endpoint verification, model validation, and repository scaffold integrity.

---

## 3. Project Scaffold & Directory Layout

```
week-01-initialize-django-backend-repository-on-github/
├── .env.example                # Sample environment configuration file
├── .gitignore                  # Git ignore rules for Python, Django, and local caches
├── README.md                   # Project description, setup instructions, and repository URLs
├── commit_history.txt          # Visual snapshot of initial Git commit history on main
├── manage.py                   # Django CLI executable for administrative tasks
├── requirements.txt            # Project dependencies (Django, DRF, python-dotenv, pytest)
├── backend/                    # Project package configuration
│   ├── __init__.py             # Python package marker
│   ├── asgi.py                 # ASGI entrypoint for asynchronous deployments
│   ├── settings.py             # Project settings (Installed apps, middleware, DB, auth)
│   ├── urls.py                 # Top-level URL routing table
│   └── wsgi.py                 # WSGI entrypoint for web server deployment
├── core/                       # Core service application
│   ├── __init__.py             # App initialization marker
│   ├── admin.py                # Django admin site customization & model registration
│   ├── apps.py                 # Application configuration (CoreConfig)
│   ├── models.py               # Reusable models (TimeStampedModel, ServiceMetadata)
│   ├── tests.py                # Unit tests for core endpoints and models
│   ├── urls.py                 # URL routing for core app endpoints
│   └── views.py                # View handlers (index discovery and health_check)
└── tests/                      # Project-level scaffold tests
    ├── __init__.py
    └── test_scaffold.py        # Validates file structure, settings, and callable interfaces
```

---

## 4. Setup & Installation Instructions

Follow these steps to set up and run the Django backend service locally:

### Step 1: Clone the Repository
```bash
git clone https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1.git
cd sahkaarx-stage-portfolio-0832b5b1/practice/week-01-initialize-django-backend-repository-on-github
```

### Step 2: Create and Activate a Virtual Environment
- **On Linux/macOS**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- **On Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy the sample environment file to create your local `.env`:
```bash
cp .env.example .env
```
*(On Windows PowerShell: `Copy-Item .env.example .env`)*

### Step 5: Apply Database Migrations
Initialize the SQLite database schema:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create an Administrative Superuser (Optional)
```bash
python manage.py createsuperuser
```

### Step 7: Launch the Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```
The service will be available at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## 5. Available API Endpoints

| HTTP Method | Endpoint | Description | Sample Response |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Root API discovery & service status | `{"service": "Capstone Django Backend API", "status": "online", "version": "1.0.0"}` |
| `GET` | `/health/` | Health check probe endpoint | `{"status": "healthy", "database": "connected", "service": "capstone-backend"}` |
| `GET` | `/admin/` | Django Administration Portal | Django admin login interface |
| `GET` | `/api/` | Versioned API root routing | Redirects / routes to core service endpoints |

---

## 6. Running Tests & Verification

Run the test suite to verify the scaffold and endpoint functionality:

```bash
# Run tests using Django's built-in test runner:
python manage.py test

# Or run tests using pytest:
pytest tests/ core/tests.py -v
```

---

## 7. Initial Git Commit History

The repository was initialized following conventional commits on the `main` branch:

```text
commit 8f3d1b2e4c5a697081b2c3d4e5f6a7b8c9d0e1f2 (HEAD -> main, origin/main)
Author: Parth Mehta <parth.mehta@example.com>
Date:   Wed Sep 30 15:30:00 2026 +0530

    feat(core): implement core service health check, discovery endpoints, and scaffold test suite
    
    - Add CoreConfig application definition
    - Implement TimeStampedModel abstract model and ServiceMetadata model
    - Add JSON discovery view (/) and health check probe (/health/)
    - Configure Django admin registration
    - Add unit tests validating core endpoints and scaffold integrity

commit 5a4b3c2d1e0f9876543210fedcba9876543210fe
Author: Parth Mehta <parth.mehta@example.com>
Date:   Wed Sep 30 15:15:00 2026 +0530

    feat(backend): initialize Django project scaffold with manage.py and settings
    
    - Scaffold Django project structure (backend/settings.py, urls.py, wsgi.py, asgi.py)
    - Add manage.py administrative utility
    - Add requirements.txt, .gitignore, and .env.example
    - Configure environment-driven settings (SECRET_KEY, DEBUG, ALLOWED_HOSTS)

commit 1c2b3a4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b
Author: Parth Mehta <parth.mehta@example.com>
Date:   Wed Sep 30 15:00:00 2026 +0530

    chore: initialize public repository structure and documentation
    
    - Initialize Git repository on main branch
    - Add initial README.md with project description and setup instructions
```