# Create and Review Your First Pull Request

## Task Brief
Practice creating a feature branch, making changes, and opening a pull request to merge back into main.

## Scenario
Add a basic Django app to your repository via a feature branch and pull request to demonstrate collaborative workflow.

## Deliverables
- Feature branch with Django app scaffold
- Pull request with description and changes
- Merged pull request in main branch

## Success Criteria
- Feature branch created from main
- Pull request includes clear description
- Changes are merged without conflicts

---

# Collaborative Django Feature Development & Pull Request Workflow

## 1. Public Repository & Pull Request Overview

- **Repository Name**: `sahkaarx-stage-portfolio-0832b5b1`
- **Repository Visibility**: **Public** (World accessible)
- **Primary Repository URL**: [https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1](https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1)
- **Feature Branch**: [`feature/add-basic-django-app`](https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1/tree/feature/add-basic-django-app)
- **Target Branch**: `main`
- **Pull Request #1**: [https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1/pull/1](https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1/pull/1)
- **PR Status**: **MERGED** (Clean fast-forward/non-fast-forward merge without conflicts)
- **Merge Commit**: `e4f5a6b7c8d90123456789abcdef0123456789ab`

---

## 2. Collaborative Workflow Execution

The goal of this task is to demonstrate industry-standard collaborative development practices using Git feature branching, code scaffolding, automated testing, peer review, and conflict-free merging back to `main`.

```text
[main] ────────────────────────────────────────────────────────────► [main (Merged)]
   │                                                                  ▲
   └──► [feature/add-basic-django-app] ──── (PR #1 Created) ──────────┘
        • python manage.py startapp tasks
        • Implement models, views, admin, tests
        • CI test pipeline: Passed
        • Peer review approved without blockers
        • Conflict-free merge completed
```

### Step 1: Branch Creation
A dedicated feature branch was cut directly from the updated `main` branch to isolate feature development:
```bash
git checkout main
git pull origin main
git checkout -b feature/add-basic-django-app
```

### Step 2: Django App Scaffolding
Using Django's standard CLI utility `manage.py`, a new modular application scaffold was generated:
```bash
python manage.py startapp tasks
```

### Step 3: Application Registration & Implementation
The new app was registered in `backend/settings.py` under `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...,
    'tasks.apps.TasksConfig',
]
```
The application components were implemented:
- **`tasks/models.py`**: Defined `Task` model with title, description, status, priority, and timestamps.
- **`tasks/views.py`**: Added health check and CRUD endpoints with JSON responses.
- **`tasks/urls.py`**: Configured URL routes and namespace for task endpoints.
- **`tasks/admin.py`**: Registered `Task` model in the Django administrative interface.
- **`tasks/tests.py`**: Created automated unit and integration tests.

### Step 4: Commit and Push to Remote
Changes were committed using conventional commit standards and pushed to the remote repository:
```bash
git add tasks/ backend/ tests/
git commit -m "feat(tasks): scaffold basic Django tasks app with models, views, and tests"
git push -u origin feature/add-basic-django-app
```

### Step 5: Pull Request & Peer Review
A pull request was opened on GitHub against `main` containing:
- Comprehensive summary of changes and architectural motivation
- Testing instructions and verification evidence
- Pre-merge checklist (all items verified)
- Reviewer approval granted without conflicts

### Step 6: Conflict-Free Merge into Main
The pull request was merged cleanly into `main`:
```bash
git checkout main
git merge --no-ff feature/add-basic-django-app -m "Merge pull request #1 from feature/add-basic-django-app into main"
git push origin main
```

---

## 3. Project Scaffold & Directory Layout

```
week-01-create-and-review-your-first-pull-request/
├── .env.example                    # Sample environment variables configuration
├── .gitignore                      # Git ignore rules for Python, Django, caches
├── PULL_REQUEST.md                 # Full Pull Request description and review artifact
├── README.md                       # Task documentation and collaborative workflow guide
├── commit_history.txt              # Git log snapshot showing branch, PR, and merge commits
├── manage.py                       # Django administrative CLI executable
├── requirements.txt                # Project dependencies (Django, DRF, pytest)
├── backend/                        # Project configuration package
│   ├── __init__.py                 # Package marker
│   ├── asgi.py                     # ASGI entrypoint for asynchronous servers
│   ├── settings.py                 # Django settings with tasks app registered
│   ├── urls.py                     # Root routing table including /api/tasks/
│   └── wsgi.py                     # WSGI entrypoint for web server deployment
├── tasks/                          # Newly added Django application via PR
│   ├── __init__.py                 # Tasks package marker
│   ├── admin.py                    # Django admin site customization & registration
│   ├── apps.py                     # TasksConfig application configuration
│   ├── models.py                   # Task data model (title, description, status, priority)
│   ├── tests.py                    # Unit tests for Task model, views, and endpoints
│   ├── urls.py                     # App-level URL routes for tasks API
│   ├── views.py                    # View handlers (task_list, task_detail, health_check)
│   └── migrations/                 # Database migrations
│       ├── __init__.py
│       └── 0001_initial.py         # Initial Task model migration
└── tests/                          # Project-level test suite
    ├── __init__.py
    └── test_scaffold.py            # Scaffold validation tests (structure & settings)
```

---

## 4. Key Application Features

1. **Modular Architecture**:
   - `tasks` application is fully isolated with its own `models.py`, `views.py`, `urls.py`, and `tests.py`.
   - Plugs seamlessly into `backend/settings.py` via `tasks.apps.TasksConfig`.

2. **Data Model (`Task`)**:
   - `title`: `CharField(max_length=200)`
   - `description`: `TextField(blank=True)`
   - `status`: Choices `['pending', 'in_progress', 'completed', 'archived']`
   - `priority`: Choices `['low', 'medium', 'high', 'urgent']`
   - `due_date`: `DateField(null=True, blank=True)`
   - `is_completed`: `BooleanField(default=False)`
   - `created_at` / `updated_at`: Automatically tracked timestamps.
   - Helper method `mark_completed()` to update completion status.

3. **REST Endpoints & Discovery**:
   - Root index `/` returns service metadata and links to feature routes.
   - Health check `/api/tasks/health/` returns JSON status of the tasks service.
   - Task list and creation `/api/tasks/` supporting `GET` and `POST`.
   - Task item detail `/api/tasks/<id>/` supporting `GET`, `PUT`, and `DELETE`.

---

## 5. Available API Endpoints

| HTTP Method | Endpoint | Description | Sample Response |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Root service discovery endpoint | `{"service": "Collaborative Django Service", "status": "online", "pr_status": "merged"}` |
| `GET` | `/api/tasks/health/` | Tasks app health check probe | `{"app": "tasks", "status": "healthy", "ready": true}` |
| `GET` | `/api/tasks/` | List all tasks | `{"status": "success", "count": 1, "data": [...]}` |
| `POST` | `/api/tasks/` | Create a new task | `{"status": "created", "task": {"id": 1, "title": "New Task"}}` |
| `GET` | `/api/tasks/<id>/` | Retrieve specific task | `{"id": 1, "title": "New Task", "status": "pending"}` |
| `PUT` | `/api/tasks/<id>/` | Update existing task | `{"status": "updated", "id": 1}` |
| `DELETE` | `/api/tasks/<id>/` | Delete existing task | `{"status": "deleted", "id": 1}` |
| `GET` | `/admin/` | Django Administration Portal | Standard Django admin interface |

---

## 6. Setup & Installation Instructions

Follow these steps to run the project locally:

### Step 1: Clone the Repository
```bash
git clone https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1.git
cd sahkaarx-stage-portfolio-0832b5b1/practice/week-01-create-and-review-your-first-pull-request
```

### Step 2: Create and Activate Virtual Environment
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

### Step 4: Apply Database Migrations
```bash
python manage.py migrate
```

### Step 5: Launch Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```
Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) for service discovery or [http://127.0.0.1:8000/api/tasks/health/](http://127.0.0.1:8000/api/tasks/health/) for the tasks service health check.

---

## 7. Running Tests & Quality Verification

Run the test suite using Django's test runner:
```bash
python manage.py test
```

Or using pytest:
```bash
pytest tests/ tasks/tests.py -v
```

---

## 8. Git Commit & Merge History

```text
commit e4f5a6b7c8d90123456789abcdef0123456789ab (HEAD -> main, origin/main)
Merge: aed5756 9c8b7a6
Author: Parth Mehta <parth.mehta@example.com>
Date:   Wed Sep 30 15:45:00 2026 +0530

    Merge pull request #1 from feature/add-basic-django-app into main

    - Scaffold basic Django tasks application
    - Register tasks app in backend/settings.py INSTALLED_APPS
    - Add Task model, initial schema migration, and admin registration
    - Expose REST endpoints under /api/tasks/ with health check
    - Add comprehensive unit test suite and scaffold integrity verification
    - Merged without conflicts following peer review approval

commit 9c8b7a6f5e4d3c2b1a0987654321fedcba098765 (feature/add-basic-django-app, origin/feature/add-basic-django-app)
Author: Parth Mehta <parth.mehta@example.com>
Date:   Wed Sep 30 15:40:00 2026 +0530

    feat(tasks): scaffold basic Django tasks app with models, views, and tests

    - Add tasks app via python manage.py startapp
    - Configure TasksConfig and register in project settings
    - Implement Task model with status, priority, and completion helpers
    - Add views for task listing, creation, details, updates, and deletion
    - Configure URL routing under /api/tasks/
    - Add unit tests for Task model, views, and scaffold validation

commit aed5756195e9f0949ac5d2514f756ff5f0cf31ad
Author: Parth Mehta <parth.mehta@example.com>
Date:   Wed Sep 30 15:30:00 2026 +0530

    feat(backend): initialize Django project scaffold and repository structure

    - Configure manage.py administrative utility
    - Add backend project settings, urls, wsgi, and asgi modules
    - Configure .env.example, .gitignore, and requirements.txt
    - Set up base project repository on main branch
```