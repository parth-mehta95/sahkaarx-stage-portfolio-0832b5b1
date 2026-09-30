# PowerShell automation script for Week 04 feature branches and atomic commits
$ErrorActionPreference = "Stop"

Write-Host "=== Setting up Git configuration ==="
git config user.name "Parth Mehta"
git config user.email "parth.mehta@ttpl.ind.in"

Write-Host "=== Staging and Committing Scaffold on main ==="
git checkout main
git add practice/week-04-implement-multiple-feature-branches-with-atomic/manage.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/requirements.txt
git add practice/week-04-implement-multiple-feature-branches-with-atomic/.env.example
git add practice/week-04-implement-multiple-feature-branches-with-atomic/.gitignore
git add practice/week-04-implement-multiple-feature-branches-with-atomic/backend/
git add practice/week-04-implement-multiple-feature-branches-with-atomic/core/
git add practice/week-04-implement-multiple-feature-branches-with-atomic/tests/

$status = git status --porcelain
if ($status) {
    git commit -m "feat(scaffold): initialize week 04 Django backend scaffold with modular architecture"
}

Write-Host "=== Creating Branch 1: feature/auth-setup ==="
# Check if branch exists locally or remotely
$localBranch = git branch --list feature/auth-setup
if ($localBranch) {
    git checkout feature/auth-setup
} else {
    git checkout -b feature/auth-setup main
}

# Commit 1
git add practice/week-04-implement-multiple-feature-branches-with-atomic/authentication/__init__.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/authentication/apps.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/authentication/config.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/authentication/tokens.py
git commit -m "feat(auth): configure JWT authentication settings and token security credentials"

# Commit 2
git add practice/week-04-implement-multiple-feature-branches-with-atomic/authentication/models.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/authentication/serializers.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/authentication/permissions.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/authentication/views.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/authentication/urls.py
git commit -m "feat(auth): implement user authentication serializers, views, and routing"

# Commit 3
git add practice/week-04-implement-multiple-feature-branches-with-atomic/authentication/tests.py
git commit -m "test(auth): add unit and integration test suite for authentication flows"

Write-Host "=== Pushing feature/auth-setup ==="
git push -u origin feature/auth-setup

Write-Host "=== Creating Branch 2: feature/database-models ==="
git checkout main
$localBranch2 = git branch --list feature/database-models
if ($localBranch2) {
    git checkout feature/database-models
} else {
    git checkout -b feature/database-models main
}

# Commit 1
git add practice/week-04-implement-multiple-feature-branches-with-atomic/database_models/__init__.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/database_models/apps.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/database_models/models.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/database_models/admin.py
git commit -m "feat(models): implement workspace and project domain database models"

# Commit 2
git add practice/week-04-implement-multiple-feature-branches-with-atomic/database_models/validators.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/database_models/views.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/database_models/urls.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/database_models/migrations/
git commit -m "feat(models): add model validations, indexes, and initial database migrations"

# Commit 3
git add practice/week-04-implement-multiple-feature-branches-with-atomic/database_models/tests.py
git commit -m "test(models): add test suite for model integrity, constraints, and audit logging"

Write-Host "=== Pushing feature/database-models ==="
git push -u origin feature/database-models

Write-Host "=== Creating Branch 3: feature/api-endpoints ==="
git checkout main
$localBranch3 = git branch --list feature/api-endpoints
if ($localBranch3) {
    git checkout feature/api-endpoints
} else {
    git checkout -b feature/api-endpoints main
}

# Commit 1
git add practice/week-04-implement-multiple-feature-branches-with-atomic/api_endpoints/__init__.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/api_endpoints/apps.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/api_endpoints/pagination.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/api_endpoints/serializers.py
git commit -m "feat(api): implement REST serializers and pagination for project endpoints"

# Commit 2
git add practice/week-04-implement-multiple-feature-branches-with-atomic/api_endpoints/filters.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/api_endpoints/views.py
git add practice/week-04-implement-multiple-feature-branches-with-atomic/api_endpoints/urls.py
git commit -m "feat(api): implement viewsets, query filters, and routing for project resources"

# Commit 3
git add practice/week-04-implement-multiple-feature-branches-with-atomic/api_endpoints/tests.py
git commit -m "test(api): add comprehensive integration test suite for REST API endpoints"

Write-Host "=== Pushing feature/api-endpoints ==="
git push -u origin feature/api-endpoints

Write-Host "=== Merging branches into main cleanly ==="
git checkout main
git merge --no-ff feature/auth-setup -m "Merge branch 'feature/auth-setup' into main"
git merge --no-ff feature/database-models -m "Merge branch 'feature/database-models' into main"
git merge --no-ff feature/api-endpoints -m "Merge branch 'feature/api-endpoints' into main"

Write-Host "=== Pushing updated main branch ==="
git push origin main

Write-Host "=== All tasks completed successfully! ==="
