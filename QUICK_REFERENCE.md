# ⚡ Quick Reference: Standard Development Workflow

## Daily Workflow (Multiple Commits)

### Standard Flow
```bash
# 1. Make changes to your code
# ... edit files ...

# 2. Stage and commit
git add .
git commit -m "Your descriptive commit message"

# 3. Push to GitHub
git push

# ✅ AUTOMATIC: Tests run locally (30 seconds)
# ✅ AUTOMATIC: If tests pass, push proceeds
# ✅ AUTOMATIC: CI pipeline runs on GitHub (2-3 minutes)
```

### What Happens Automatically

```
You type: git push
    ↓
[LOCAL] Pre-push hook runs
    ↓
[LOCAL] All 51 tests execute (~30 seconds)
    ↓
    ├─ ✅ Tests pass → Push proceeds
    │       ↓
    │   [GITHUB] Code pushed
    │       ↓
    │   [GITHUB] CI Pipeline runs
    │       ↓
    │   [GITHUB] Tests on Python 3.9, 3.10, 3.11
    │       ↓
    │   [GITHUB] Code quality checks
    │       ↓
    │   [GITHUB] Security scans
    │       ↓
    │   ✅ All checks pass → Ready for deployment
    │
    └─ ❌ Tests fail → Push blocked
            ↓
        Fix issues locally
            ↓
        Try again: git push
```

## What You See

### Successful Push ✅
```
Running tests before push...

Running all regression tests...
...
Ran 51 tests in 1.220s

OK (skipped=2)

[SUCCESS] All tests passed! Proceeding with push...

Enumerating objects: 5, done.
...
To https://github.com/jeffbecraft/VibeCoding_BaseballAnalysis.git
   abc1234..def5678  master -> master
```

### Failed Local Tests ❌
```
Running tests before push...

Running all regression tests...
...
FAIL: test_something

[FAILED] Tests failed! Push aborted.
   Fix the failing tests before pushing to remote.

To skip this check (not recommended), use:
   git push --no-verify
```

## Manual Testing (Optional)

### Run Tests Anytime
```bash
# Full test suite
python run_tests.py

# Specific test file
python -m pytest tests/test_data_fetcher.py -v

# With coverage
python -m pytest --cov=src tests/
```

## Emergency Override (Use Sparingly!)

```bash
# Skip local tests (not recommended)
git push --no-verify
```
⚠️ **Warning:** This will likely cause CI to fail!

## Check CI Status

### Command Line
```bash
# See recent runs
gh run list

# Watch current run
gh run watch

# View specific workflow
gh workflow view "CI Pipeline"
```

### Web Browser
- **All Runs:** https://github.com/jeffbecraft/VibeCoding_BaseballAnalysis/actions
- **CI Workflow:** https://github.com/jeffbecraft/VibeCoding_BaseballAnalysis/actions/workflows/ci.yml

## Time Savings

### Before Pre-Push Hook
```
Edit → Commit → Push → Wait 2-3 min → CI fails → Fix → Push → Wait 2-3 min → CI passes
Total: 5-10 minutes
```

### After Pre-Push Hook
```
Edit → Commit → Push → Tests pass locally (30 sec) → CI passes
Total: 30 seconds + 2-3 min CI (running in background)
```

**You get feedback in 30 seconds instead of 2-3 minutes!**

## Best Practices

1. ✅ **Let the hook run** - It's your first line of defense
2. ✅ **Commit often** - Small, focused commits
3. ✅ **Push regularly** - Don't accumulate commits
4. ✅ **Fix immediately** - Don't ignore test failures
5. ✅ **Meaningful messages** - Describe what changed
6. ❌ **Avoid --no-verify** - Use only in emergencies

## Multi-Commit Days

Making multiple commits per day? Perfect! The workflow handles it:

```bash
# Morning: Feature work
git commit -m "Add player comparison feature"
git push  # ✅ Tests pass locally → Push proceeds

# Noon: Bug fix
git commit -m "Fix date parsing issue"
git push  # ✅ Tests pass locally → Push proceeds

# Afternoon: Refactoring
git commit -m "Refactor cache management"
git push  # ✅ Tests pass locally → Push proceeds

# Each push:
# - Tests run locally first (30 sec)
# - Only proceeds if tests pass
# - CI validates on GitHub (2-3 min)
```

## Summary

**Your Standard Flow:**
1. Code
2. Commit
3. Push → Tests run automatically
4. CI validates on GitHub

**Benefits:**
- ✅ Fast feedback (30 seconds)
- ✅ Confidence before pushing
- ✅ Fewer failed CI runs
- ✅ Professional workflow

---

**Setup:** ✅ Complete  
**Hook Status:** ✅ Active  
**Ready for:** Multiple daily commits!
