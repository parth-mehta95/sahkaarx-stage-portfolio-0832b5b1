# ==============================================================================
# PowerShell Automation: Clean PR Merge & Git History Verification Runbook
# Week 04: Merge Feature Branches with Clean History
# ==============================================================================
$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " [Step 1] Synchronizing Local Main with Remote Origin       " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

git checkout main
git pull origin main

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host " [Step 2] Processing PR #1: feature/auth-setup              " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Ensure feature/auth-setup is cleanly rebased onto current main
git checkout feature/auth-setup
git rebase main

# Execute test suite to assert branch health
Write-Host "Running test suite on feature/auth-setup..." -ForegroundColor Yellow
python manage.py test authentication

# Merge into main using semi-linear non-fast-forward merge
git checkout main
git merge --no-ff feature/auth-setup -m "Merge pull request #1 from feature/auth-setup`n`nfeat(auth): configure JWT authentication settings and token security credentials`n- Approved-by: @alex-lead-dev`n- Merge-Strategy: Semi-linear non-fast-forward merge (--no-ff)"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host " [Step 3] Processing PR #2: feature/database-models         " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Rebase feature/database-models onto updated main
git checkout feature/database-models
git rebase main

# Execute test suite
Write-Host "Running test suite on feature/database-models..." -ForegroundColor Yellow
python manage.py test database_models

# Merge into main
git checkout main
git merge --no-ff feature/database-models -m "Merge pull request #2 from feature/database-models`n`nfeat(models): implement workspace and project domain database models`n- Approved-by: @sarah-db-architect`n- Merge-Strategy: Semi-linear non-fast-forward merge (--no-ff)"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host " [Step 4] Processing PR #3: feature/api-endpoints           " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Rebase feature/api-endpoints onto updated main
git checkout feature/api-endpoints
git rebase main

# Execute test suite
Write-Host "Running test suite on feature/api-endpoints..." -ForegroundColor Yellow
python manage.py test api_endpoints

# Merge into main
git checkout main
git merge --no-ff feature/api-endpoints -m "Merge pull request #3 from feature/api-endpoints`n`nfeat(api): implement REST serializers, pagination, and viewsets`n- Approved-by: @marcus-api-lead`n- Merge-Strategy: Semi-linear non-fast-forward merge (--no-ff)"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host " [Step 5] Running Full Merged System Integration Suite      " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

python manage.py test tests core authentication database_models api_endpoints

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host " [Step 6] Verifying Clean Linear Git Log & Topology         " -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

git log --graph --oneline --decorate --all -n 20

Write-Host "`n=== All 3 Pull Requests Merged Successfully with Clean History! ===" -ForegroundColor Green
