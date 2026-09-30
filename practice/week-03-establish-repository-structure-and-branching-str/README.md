# Establish Repository Structure and Branching Strategy

## Task Brief
Implement professional repository organization, establish branching conventions, and create documentation for team collaboration standards.

## Scenario
Your backend team needs clear repository standards. Organize the Django project structure, define branching strategy, and document in README.

## Deliverables
- Organized Django project structure
- README with branching strategy
- Development setup instructions

## Success Criteria
- Project structure follows Django conventions
- Branching strategy documented clearly
- Setup guide enables new team members

---

# Backend Engineering: Repository Architecture & Team Branching Strategy

## 1. Executive Overview & Repository Metadata

This module establishes the official enterprise repository architecture, modular Django structure, cross-cutting utilities, Git branching workflow, and onboarding setup instructions for the **Capstone Django Backend Service**.

- **Repository**: `sahkaarx-stage-portfolio-0832b5b1`
- **Visibility**: **Public** (World accessible)
- **GitHub Repository URL**: [https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1](https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1)
- **Module Path**: [`practice/week-03-establish-repository-structure-and-branching-str`](.)
- **Primary Branches**: `main` (Production), `develop` (Integration & Staging)
- **Branching Guide**: [`BRANCHING_STRATEGY.md`](BRANCHING_STRATEGY.md)
- **Commit History Record**: [`commit_history.txt`](commit_history.txt)

---

## 2. Organized Django Project Architecture

The codebase adheres strictly to the **Separation of Concerns (SoC)** and the **Single Responsibility Principle (SRP)** by isolating configuration packages, foundation models, domain business logic, centralized cross-cutting utilities, and test suites.

### Complete Directory Scaffold Layout

```text
week-03-establish-repository-structure-and-branching-str/
├── .env.example                       # Sample environment configuration template
├── .gitignore                         # Git exclusion rules for Python, Django, and OS caches
├── BRANCHING_STRATEGY.md              # Dedicated team branching guidelines and review policies
├── commit_history.txt                 # Git log snapshot documenting atomic implementation commits
├── manage.py                          # Django administrative CLI executable
├── README.md                          # Repository structure, branching strategy, and setup documentation
├── requirements.txt                   # Production and testing Python dependencies
│
├── backend/                           # Project configuration package
│   ├── __init__.py                    # Package marker
│   ├── asgi.py                        # ASGI entrypoint for asynchronous and WebSocket servers
│   ├── settings.py                    # Centralized settings with environment-driven variable overrides
│   ├── urls.py                        # Root URL routing table delegating to apps
│   └── wsgi.py                        # WSGI entrypoint for HTTP application servers (Gunicorn/uWSGI)
│
├── core/                              # Foundational infrastructure application
│   ├── __init__.py                    # App package marker
│   ├── admin.py                       # Admin site registration for infrastructure models
│   ├── apps.py                        # App configuration (CoreConfig)
│   ├── models.py                      # Reusable models (TimeStampedModel, ServiceMetadata)
│   ├── tests.py                       # Unit tests for core endpoints and models
│   ├── urls.py                        # Routing for health, ping, and root discovery
│   └── views.py                       # Health check probe, liveness ping, and service info
│
├── tasks/                             # Business domain application
│   ├── __init__.py                    # App package marker
│   ├── admin.py                       # ModelAdmin configuration with filters and search
│   ├── apps.py                        # App configuration (TasksConfig)
│   ├── models.py                      # Task and TaskCategory domain models
│   ├── serializers.py                 # Django REST Framework serializers with custom validation
│   ├── services.py                    # Decoupled domain service layer (TaskService)
│   ├── tests.py                       # Unit and integration tests for tasks API and services
│   ├── urls.py                        # API route mappings (/api/tasks/)
│   └── views.py                       # REST API views with pagination and filtering
│
├── utils/                             # Centralized utilities & cross-cutting concerns
│   ├── __init__.py                    # Utilities package exports
│   ├── constants.py                   # Enumerations (TaskStatus, TaskPriority, HttpStatusCodes)
│   ├── exceptions.py                  # Custom DRF exception handler returning uniform JSON envelopes
│   ├── helpers.py                     # String slugs, UUID reference IDs, ISO timestamp formatters
│   ├── pagination.py                  # StandardResultsSetPagination with total page counts
│   └── validators.py                  # Title sanitation, placeholder detection, future date checks
│
└── tests/                             # Project-level scaffold test suite
    ├── __init__.py                    # Tests package marker
    ├── test_project_structure.py      # Verifies presence and organization of all directory components
    └── test_scaffold.py               # Verifies Django settings, INSTALLED_APPS, and URL resolutions
```

---

## 3. Component Responsibility Breakdown

### A. Project Configuration (`backend/`)
- **`settings.py`**: Separates settings into `DJANGO_APPS`, `THIRD_PARTY_APPS`, and `LOCAL_APPS`. Reads sensitive values (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`) securely from environment variables. Configures REST Framework to use our custom pagination and exception handling.
- **`urls.py`**: Clean top-level routing that namespaces `/admin/`, `/` (delegated to `core.urls`), and `/api/tasks/` (delegated to `tasks.urls`).
- **`wsgi.py` & `asgi.py`**: Clean deployment gateways for standard WSGI and ASGI servers.

### B. Core Infrastructure App (`core/`)
- **`TimeStampedModel`**: An abstract base model providing `created_at` and `updated_at` timestamps. All domain models across the codebase inherit from this class to ensure consistent auditability.
- **`ServiceMetadata`**: Operational model tracking service version, environment name, and health state.
- **System Endpoints**:
  - `GET /`: Service discovery returning service name, version, and routing index.
  - `GET /health/`: Probes database connectivity, measures latency in milliseconds, and returns operational state.
  - `GET /ping/`: Minimal overhead liveness probe returning `{"status": "pong"}` for load balancers.

### C. Domain Application (`tasks/`)
- **`models.py`**: `Task` and `TaskCategory` models equipped with human-readable reference IDs (e.g. `TSK-XXXX`), status choices, priority tiers, assigned team members, and deadline tracking.
- **`services.py`**: Encapsulates all domain business logic inside `TaskService`. Separating business workflows from views prevents fat views and ensures business rules (e.g. status transition constraints, metric calculations) can be reused in celery workers, CLI commands, or REST APIs.
- **`serializers.py`**: Validates request data using centralized validators and converts domain models into structured JSON.
- **`views.py`**: REST API endpoints for listing, creating, retrieving, updating (PATCH), deleting, and aggregating metrics.

### D. Centralized Utilities (`utils/`)
- **`constants.py`**: Enums for `TaskStatus` (`pending`, `in_progress`, `completed`, `cancelled`, `blocked`), `TaskPriority` (`low`, `medium`, `high`, `critical`), and standard HTTP status code references.
- **`exceptions.py`**: Custom exception handler `custom_exception_handler` intercepting both Django validation errors and DRF exceptions, producing uniform error responses:
  ```json
  {
    "success": false,
    "status_code": 400,
    "error_code": "VALIDATION_FAILED",
    "message": "Task title cannot be empty or purely whitespace.",
    "details": {...}
  }
  ```
- **`pagination.py`**: `StandardResultsSetPagination` providing a standardized response envelope:
  ```json
  {
    "success": true,
    "pagination": {
      "count": 42,
      "total_pages": 5,
      "current_page": 1,
      "page_size": 10,
      "next": "http://localhost:8000/api/tasks/?page=2",
      "previous": null
    },
    "results": [...]
  }
  ```
- **`validators.py`**: Reusable validation rules checking for placeholder titles (e.g. `test`, `untitled`), minimum string lengths, and past due date validation.
- **`helpers.py`**: Common utilities for ID generation (`generate_reference_id`), string slugification (`slugify_text`), and timestamp formatting (`format_iso_timestamp`).

---

## 4. Official Team Branching Strategy

Our team utilizes an enhanced **GitHub Flow / Trunk-Based hybrid** model designed for rapid feature delivery while maintaining strict production stability.

### Branch Topology Diagram

```text
[main] (Production: v1.0.0) ───────────────────────────────────────────────► [main: v1.1.0]
  │                                                                              ▲
  │ (Initial branch)                                                             │ (Release PR)
  ▼                                                                              │
[develop] (Staging) ─────────┬────────────────────────┬────────► [develop] ──────┤
  │                          │                        │            ▲             │
  │                          ▼                        ▼            │             ▼
  │               [feature/backend-104]    [feature/backend-105]   │     [hotfix/backend-110]
  │                          │                        │            │     (Emergency patch)
  │                          ▼                        ▼            │             │
  └──────────────────► (PR #1: Squash)       (PR #2: Squash) ──────┘             └──► [main & dev]
```

### Branch Taxonomy

| Branch Category | Base Branch | Target Branch | Merging Strategy | Review SLA |
| :--- | :--- | :--- | :--- | :--- |
| **`main`** | *N/A* | *N/A* | Protected (No direct pushes) | N/A |
| **`develop`** | `main` | `main` | Protected (PR only) | 24 Hours |
| **`feature/*`** | `develop` | `develop` | **Squash and Merge** | 12 Hours |
| **`bugfix/*`** | `develop` | `develop` | **Squash and Merge** | 6 Hours |
| **`hotfix/*`** | `main` | `main` & `develop` | **Merge Commit (`--no-ff`)** | 2 Hours (Urgent) |
| **`release/*`** | `develop` | `main` & `develop` | **Merge Commit (`--no-ff`)** | 12 Hours |

### Branch Naming Conventions
All branch names must be prefixed by work type and reference the corresponding ticketing identifier:
- **Features**: `feature/<ticket-id>-<short-description>` (e.g., `feature/TSK-101-task-service-layer`)
- **Bug Fixes**: `bugfix/<ticket-id>-<short-description>` (e.g., `bugfix/TSK-108-fix-due-date-validation`)
- **Refactoring**: `refactor/<ticket-id>-<short-description>` (e.g., `refactor/TSK-115-modularize-utils`)
- **Hotfixes**: `hotfix/<ticket-id>-<short-description>` (e.g., `hotfix/TSK-120-cors-header-fix`)
- **Releases**: `release/v<major>.<minor>.<patch>` (e.g., `release/v1.1.0`)

### Conventional Commits 1.0.0 Specification
All commit messages must adhere to the Conventional Commits specification:
```text
<type>(<scope>): <subject>

[optional body explaining context, why this change was made, and alternatives considered]

[optional footer(s) referencing issue tracker tickets or BREAKING CHANGES]
```

**Permitted Types**:
- `feat`: A new feature or capability.
- `fix`: A bug fix or patch.
- `docs`: Documentation-only updates.
- `style`: Formatting, whitespace adjustments, lint fixes with no behavior changes.
- `refactor`: Code restructuring without fixing bugs or adding new features.
- `perf`: Performance optimizations.
- `test`: Adding or modifying automated test suites.
- `chore`: Dependency updates, tooling configuration, build scripts.

### Pull Request (PR) Lifecycle
1. **Branch Creation**: Engineer creates branch from updated `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/TSK-101-task-service-layer
   ```
2. **Local Development & Testing**: Code is written, tested, formatted with `black`, and checked with `flake8`.
3. **Rebase Before PR**: Engineer rebases onto `origin/develop` to eliminate divergence:
   ```bash
   git fetch origin
   git rebase origin/develop
   ```
4. **Open PR**: PR title must mirror the conventional commit format with a filled PR template (description, testing proof, risk assessment).
5. **Peer Review**: Minimum **1 approving review** from a senior engineer or code owner.
6. **Automated CI Checks**: All test suites must pass 100% with no regressions.
7. **Squash and Merge**: PR is squash-merged into `develop` to preserve a clean, linear history.

### Branch Protection Rules
Configured on GitHub repository settings:
- **Require PR before merging**: Enforced on `main` and `develop`.
- **Require approvals**: 2 approvals required for `main`; 1 approval required for `develop`.
- **Dismiss stale PR approvals**: Triggered on new pushes.
- **Require status checks**: CI unit test suite and linting must pass before merge button is enabled.
- **Block direct pushes & force pushes**: Strictly forbidden on `main` and `develop`.

---

## 5. Development Environment Setup Instructions

Follow these step-by-step instructions to configure and run the Django backend service locally:

### Step 1: Clone the Repository
```bash
git clone https://github.com/parth-mehta95/sahkaarx-stage-portfolio-0832b5b1.git
cd sahkaarx-stage-portfolio-0832b5b1/practice/week-03-establish-repository-structure-and-branching-str
```

### Step 2: Create and Activate Virtual Environment
- **On Linux / macOS**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- **On Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **On Windows (Command Prompt)**:
  ```cmd
  python -m venv venv
  .\venv\Scripts\activate.bat
  ```

### Step 3: Install Project Dependencies
Upgrade `pip` and install all required packages:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Local Environment Variables
Create your local `.env` file from the provided template:
```bash
# On Linux/macOS
cp .env.example .env

# On Windows PowerShell
Copy-Item .env.example .env
```
Inspect `.env` and configure settings as required for local development:
```ini
DJANGO_SECRET_KEY=local-dev-secret-key-change-in-production
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
DATABASE_URL=sqlite:///db.sqlite3
DEFAULT_PAGE_SIZE=10
```

### Step 5: Run Database Migrations
Initialize your database schema:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create an Administrative Superuser (Optional)
```bash
python manage.py createsuperuser
```

### Step 7: Start the Django Development Server
```bash
python manage.py runserver
```
The application will start on `http://127.0.0.1:8000/`.

---

## 6. Verification & API Smoke Testing

With the server running, you can test endpoints using `curl` or any REST client:

### 1. Service Discovery
```bash
curl -X GET http://127.0.0.1:8000/
```
**Response**:
```json
{
  "service": "capstone-stage-backend",
  "description": "Standardized Django Backend Service with Modular Architecture",
  "version": "1.0.0",
  "timestamp": "2026-09-30T19:45:00Z",
  "endpoints": {
    "root": "/",
    "health": "/health/",
    "ping": "/ping/",
    "tasks_api": "/api/tasks/",
    "admin": "/admin/"
  }
}
```

### 2. Health Check Probe
```bash
curl -X GET http://127.0.0.1:8000/health/
```
**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-09-30T19:45:00Z",
  "checks": {
    "database": {
      "status": "healthy",
      "latency_ms": 1.45
    },
    "service": "operational"
  }
}
```

### 3. Create a Task via API
```bash
curl -X POST http://127.0.0.1:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Implement caching layer", "description": "Configure Redis backend for frequent queries", "priority": "high"}'
```
**Response**:
```json
{
  "success": true,
  "message": "Task successfully created.",
  "data": {
    "id": 1,
    "reference_id": "TSK-8F3B91AC",
    "title": "Implement caching layer",
    "description": "Configure Redis backend for frequent queries",
    "status": "pending",
    "priority": "high",
    "category": null,
    "assigned_to": null,
    "due_date": null,
    "completed_at": null
  }
}
```

### 4. Fetch Operational Metrics
```bash
curl -X GET http://127.0.0.1:8000/api/tasks/metrics/
```
**Response**:
```json
{
  "success": true,
  "data": {
    "total_tasks": 1,
    "status_breakdown": {
      "pending": 1,
      "in_progress": 0,
      "completed": 0,
      "blocked": 0,
      "overdue": 0
    },
    "completion_rate_percentage": 0.0
  }
}
```

---

## 7. Automated Testing & Code Quality Tools

### Running Tests
Execute the full test suite using Django's test runner:
```bash
python manage.py test
```

Execute tests using `pytest` with coverage report:
```bash
pytest --cov=.
```

### Code Formatting with Black
Verify that all Python code adheres to PEP 8 standards:
```bash
black --check .
# To auto-format:
black .
```

### Linting with Flake8
Enforce clean imports, max line length (120), and syntax cleanliness:
```bash
flake8 --max-line-length=120 --exclude=venv,.git,__pycache__
```

---

## 8. Summary of Deliverables & Success Criteria Matrix

| Deliverable / Requirement | Implementation Detail | Location in Repository | Status |
| :--- | :--- | :--- | :---: |
| **Organized Django Project Structure** | Modular apps (`core`, `tasks`), configs (`backend/`), and centralized utilities (`utils/`). | [`backend/`](backend/), [`core/`](core/), [`tasks/`](tasks/), [`utils/`](utils/) | **Complete** |
| **Decoupled Service Layer** | Business logic extracted into `TaskService` away from views and serializers. | [`tasks/services.py`](tasks/services.py) | **Complete** |
| **Standardized Error & Pagination Utilities** | Uniform JSON error responses and paginated result envelopes. | [`utils/exceptions.py`](utils/exceptions.py), [`utils/pagination.py`](utils/pagination.py) | **Complete** |
| **Dedicated Branching Strategy** | Git Flow / Trunk hybrid, branch naming, Conventional Commits, PR SLA, protection rules. | [`BRANCHING_STRATEGY.md`](BRANCHING_STRATEGY.md) | **Complete** |
| **Development Setup Instructions** | Step-by-step onboarding guide from clone to curl smoke testing. | Section 5 above | **Complete** |
| **Repository Scaffold Test Suite** | Automated tests asserting presence of all directories, settings, and URLs. | [`tests/test_project_structure.py`](tests/test_project_structure.py), [`tests/test_scaffold.py`](tests/test_scaffold.py) | **Complete** |
| **Atomic Commit History** | Descriptive Conventional Commits tracking chronological scaffold setup. | [`commit_history.txt`](commit_history.txt) | **Complete** |