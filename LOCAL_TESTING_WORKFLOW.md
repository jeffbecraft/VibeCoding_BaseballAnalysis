# Local Testing Workflow

## Automatic Pre-Push Testing

This repository is configured to **automatically run tests before every push** to GitHub. This ensures:
- ✅ CI pipeline only runs when tests pass locally
- ✅ Faster feedback (local tests are quicker than CI)
- ✅ Fewer failed CI runs cluttering your history
- ✅ Confidence in every commit

## How It Works

### Pre-Push Hook
A Git hook runs automatically when you execute `git push`:

```
You type: git push
    ↓
Hook runs: python run_tests.py
    ↓
Tests pass? → Push proceeds to GitHub → CI runs
    ↓
Tests fail? → Push blocked → Fix tests locally
```

### Your Standard Workflow

```bash
# 1. Make your changes
# ... edit files ...

# 2. Commit locally
git add .
git commit -m "Your commit message"

# 3. Push to GitHub
git push

# 🔍 Hook automatically runs tests!
# ✅ If tests pass → Push proceeds
# ❌ If tests fail → Fix and try again
```

## Example Output

### When Tests Pass ✅
```
🔍 Running tests before push...

Running MLB Statistics Test Suite
==================================================

test_cache (tests.test_cache.TestCache)
Testing cache initialization ... ok
...
Ran 49 tests in 2.345s

OK (skipped=2)

✅ All tests passed! Proceeding with push...

Enumerating objects: 5, done.
...
```

### When Tests Fail ❌
```
🔍 Running tests before push...

Running MLB Statistics Test Suite
==================================================

FAIL: test_player_stats (tests.test_data_fetcher.TestDataFetcher)
...

❌ Tests failed! Push aborted.
   Fix the failing tests before pushing to remote.

To skip this check (not recommended), use:
   git push --no-verify
```

## Setup Instructions

### Initial Setup (Already Done!)
The hook is already installed. If you need to reinstall it:

```powershell
.\setup_hooks.ps1
```

### Verifying Hook is Active
```bash
# Check if hook file exists
Test-Path .git\hooks\pre-push

# Should return: True
```

## Manual Testing

You can also run tests manually anytime:

```bash
# Run full test suite
python run_tests.py

# Run specific test file
python -m pytest tests/test_data_fetcher.py

# Run with coverage
python -m pytest --cov=src tests/
```

## Advanced Options

### Skip Hook (Emergency Only)
If you absolutely need to push without running tests:

```bash
git push --no-verify
```

⚠️ **Not recommended!** This will likely cause CI to fail.

### Temporarily Disable Hook
```bash
# Rename the hook
mv .git\hooks\pre-push .git\hooks\pre-push.disabled

# Re-enable later
mv .git\hooks\pre-push.disabled .git\hooks\pre-push
```

### Run Hook Manually
```bash
# Test the hook without pushing
.git\hooks\pre-push.ps1
```

## Workflow Benefits

### Before (Without Hook)
```
Edit code → Commit → Push → CI fails → Fix → Push → CI fails → Fix → Push → CI passes
Time wasted: 10-15 minutes waiting for CI
```

### After (With Hook)
```
Edit code → Commit → Push → Tests run locally (30 seconds) → Fix if needed → Push → CI passes
Time saved: 90% faster feedback
```

## Integration with CI/CD

The pre-push hook complements the CI pipeline:

1. **Local Hook** - Fast feedback (30 seconds)
   - Runs on your machine
   - Catches obvious errors
   - Uses your local Python environment

2. **GitHub Actions CI** - Comprehensive validation (2-3 minutes)
   - Tests across Python 3.9, 3.10, 3.11
   - Code quality checks (pylint, flake8)
   - Security scans (bandit, safety)
   - Build validation

Both work together to ensure code quality!

## Customization

### Modify What Runs
Edit `.git\hooks\pre-push.ps1` to change behavior:

```powershell
# Example: Run linting before tests
& python -m flake8 src/ utils/
if ($LASTEXITCODE -ne 0) { exit 1 }

& python run_tests.py
if ($LASTEXITCODE -ne 0) { exit 1 }
```

### Add Other Checks
```powershell
# Example: Check for debug statements
$debugStatements = Select-String -Path "src/*.py" -Pattern "import pdb|breakpoint()"
if ($debugStatements) {
    Write-Host "❌ Found debug statements! Remove before pushing." -ForegroundColor Red
    exit 1
}
```

## Troubleshooting

### Hook Doesn't Run
```bash
# Check if hook is executable
Get-Content .git\hooks\pre-push

# Reinstall
.\setup_hooks.ps1
```

### Tests Hang
```bash
# Cancel with Ctrl+C
# Then skip hook if needed
git push --no-verify
```

### Virtual Environment Not Found
The hook automatically activates `.venv` if it exists. If you use a different environment:

```powershell
# Edit .git\hooks\pre-push.ps1
# Change the activation path to your environment
```

## Best Practices

1. ✅ **Let the hook run** - It's faster than waiting for CI to fail
2. ✅ **Fix tests immediately** - Don't accumulate broken tests
3. ✅ **Commit working code** - Test locally before committing
4. ✅ **Use meaningful commits** - Each commit should be a working state
5. ❌ **Don't use --no-verify** unless absolutely necessary

## Summary

Your development workflow now includes automatic testing:

```
Local Testing (pre-push hook) → GitHub Push → CI Pipeline
     30 seconds                    instant      2-3 minutes
     ↓                                          ↓
     Catches errors early                       Comprehensive validation
```

**Result:** Faster development, fewer CI failures, higher confidence! 🚀

---

**Hook Status:** ✅ Active  
**Setup Script:** `setup_hooks.ps1`  
**Hook Location:** `.git/hooks/pre-push`
