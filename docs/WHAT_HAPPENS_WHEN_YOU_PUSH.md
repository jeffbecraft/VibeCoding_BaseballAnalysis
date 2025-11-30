# What Happens When You Push Code

## Quick Reference

When you push code to the `master` or `main` branch:

```
Your Push → GitHub → Tests Run → ✓ Pass → Version Bumps → Tag Created → Auto-Commit
```

## Detailed Flow

### 1. You Make Changes and Push
```bash
# You edit some source code
vim src/data_fetcher.py

# Commit your changes
git add src/data_fetcher.py
git commit -m "fix: improve error handling"

# Push to GitHub
git push origin master
```

**Current Version**: `1.0.0`

### 2. GitHub Receives Your Push
GitHub detects:
- Push to `master` branch ✓
- Changes in monitored paths (`src/**`) ✓
- No `[skip ci]` in commit message ✓

**Action**: Trigger Auto Version Bump workflow

### 3. GitHub Actions Starts Workflow

The workflow (`.github/workflows/auto-version.yml`) executes:

```yaml
Step 1: Checkout code
  → Fetches your latest commit

Step 2: Setup Python 3.11
  → Prepares test environment

Step 3: Install dependencies
  → pip install -r requirements.txt
  → pip install pytest pytest-cov

Step 4: Run full regression test suite ⏱️
  → python run_tests.py
  → Runs all 54 tests
  → Takes ~30 seconds
```

### 4. Test Execution

```
Running Tests...
├── test_data_fetcher.py ............ (12 tests)
├── test_data_processor.py ......... (10 tests)
├── test_mlb_stats.py .............. (15 tests)
├── test_ai_query_handler.py ....... (8 tests)
├── test_comparison.py ............. (6 tests)
└── test_career.py ................. (3 tests)

Total: 54 tests
Result: ✓ All passed
```

**If tests fail**: Workflow stops here, version stays at `1.0.0`  
**If tests pass**: Continue to next step

### 5. Version Bump Happens ✨

```bash
# Workflow runs:
python scripts/bump_version.py

# Script executes:
Current version: 1.0.0
New version: 1.0.1

# Files updated:
✓ src/__init__.py       → __version__ = "1.0.1"
✓ pyproject.toml        → version = "1.0.1"
✓ CHANGELOG.md          → Added entry for 1.0.1
```

**New Version**: `1.0.1`

### 6. Changes Committed Back

```bash
# Workflow configures git
git config user.email "github-actions[bot]@users.noreply.github.com"
git config user.name "github-actions[bot]"

# Stages version files
git add src/__init__.py pyproject.toml CHANGELOG.md

# Commits with special marker (prevents infinite loop)
git commit -m "chore: bump version to 1.0.1 [auto-version]"

# Pushes back to GitHub
git push origin master
```

### 7. Git Tag Created

```bash
# Workflow creates annotated tag
git tag -a "v1.0.1" -m "Auto-generated version v1.0.1"

# Pushes tag to GitHub
git push origin v1.0.1
```

### 8. You Pull Latest Changes

```bash
# Pull the auto-commit
git pull origin master

# You'll see:
# * abc1234 (tag: v1.0.1) chore: bump version to 1.0.1 [auto-version]
# * def5678 fix: improve error handling

# Check new version
python -c "from src import __version__; print(__version__)"
# Output: 1.0.1
```

### 9. Version Visible in UI

When someone opens the Streamlit app:

```
Sidebar shows:
⚾ MLB Stats Analysis v1.0.1
```

## Complete Timeline

| Time | Event | Who | Version |
|------|-------|-----|---------|
| 0:00 | Developer commits fix | You | 1.0.0 |
| 0:01 | Push to GitHub | You | 1.0.0 |
| 0:02 | Workflow triggered | GitHub | 1.0.0 |
| 0:03 | Setup environment | GitHub Actions | 1.0.0 |
| 0:05 | Install dependencies | GitHub Actions | 1.0.0 |
| 0:10 | Run 54 tests | GitHub Actions | 1.0.0 |
| 0:40 | Tests pass ✓ | GitHub Actions | 1.0.0 |
| 0:41 | Bump version script | GitHub Actions | 1.0.1 |
| 0:42 | Commit version files | GitHub Actions | 1.0.1 |
| 0:43 | Create git tag v1.0.1 | GitHub Actions | 1.0.1 |
| 0:44 | Push to GitHub | GitHub Actions | 1.0.1 |
| 0:45 | Workflow complete ✓ | GitHub Actions | 1.0.1 |
| 0:50 | Developer pulls changes | You | 1.0.1 |

**Total time**: ~45 seconds

## What Gets Created

After one push that passes tests:

### In Git History
```bash
git log --oneline -2

# Shows:
abc1234 (HEAD -> master, tag: v1.0.1, origin/master) chore: bump version to 1.0.1 [auto-version]
def5678 fix: improve error handling
```

### In Git Tags
```bash
git tag -l

# Shows:
v1.0.0
v1.0.1  ← New tag
```

### In GitHub
- Commit visible in history
- Tag visible in Releases section
- Workflow run visible in Actions tab

### In CHANGELOG.md
```markdown
## [1.0.1] - 2025-11-30

### Changed
- Auto-incremented version from 1.0.0 after successful test execution
```

## What Triggers Auto-Versioning

### ✅ WILL Trigger
```bash
# Any push to master/main with source code changes
git push origin master

# Modified files in these paths:
src/data_fetcher.py          # Source code
utils/cache.py               # Utilities
streamlit_app.py             # Main app
requirements.txt             # Dependencies
pyproject.toml               # Project config
```

### ❌ WON'T Trigger
```bash
# 1. Commit with [skip ci]
git commit -m "docs: update README [skip ci]"

# 2. Push to other branches
git push origin develop

# 3. Changes only in non-monitored paths:
docs/guide.md                # Documentation
tests/test_new.py            # Test files
.github/workflows/ci.yml     # Workflow configs
README.md                    # Readme
.gitignore                   # Git config
```

### ❌ WON'T Trigger (Safety)
```bash
# Auto-version commits (prevents infinite loop)
git commit -m "chore: bump version to 1.0.2 [auto-version]"
# The [auto-version] marker prevents re-triggering
```

## If Tests Fail

### What Happens
```
1. Tests run
2. Some tests fail ❌
3. Workflow stops
4. Version stays at 1.0.0
5. No commit created
6. No tag created
7. GitHub shows red X on commit
```

### What You See
- Email notification: "Build failed"
- GitHub Actions tab: Red X next to workflow
- Commit in history: Red X indicator

### What To Do
```bash
# 1. Check which tests failed
# Go to GitHub → Actions → Click failed workflow → View logs

# 2. Fix the issue locally
vim src/data_fetcher.py

# 3. Test locally
python run_tests.py

# 4. Commit fix and push
git add src/data_fetcher.py
git commit -m "fix: resolve test failures"
git push origin master

# 5. Workflow runs again, this time passes
# Version increments: 1.0.0 → 1.0.1
```

## Multiple Pushes

### Scenario: Push 3 times in a row

```bash
# Push 1 (9:00 AM)
git commit -m "fix: bug A"
git push
# → Tests pass → Version: 1.0.0 → 1.0.1

# Push 2 (9:05 AM)
git commit -m "fix: bug B"
git push
# → Tests pass → Version: 1.0.1 → 1.0.2

# Push 3 (9:10 AM)
git commit -m "feat: new feature"
git push
# → Tests pass → Version: 1.0.2 → 1.0.3
```

**Result**: Each successful push increments PATCH version

### Git History
```
* abc1234 (tag: v1.0.3) chore: bump version to 1.0.3 [auto-version]
* def5678 feat: new feature
* ghi9012 (tag: v1.0.2) chore: bump version to 1.0.2 [auto-version]
* jkl3456 fix: bug B
* mno7890 (tag: v1.0.1) chore: bump version to 1.0.1 [auto-version]
* pqr1234 fix: bug A
* stu5678 (tag: v1.0.0) feat: implement auto-versioning
```

## Viewing Progress

### During Workflow Execution
1. Go to GitHub repository
2. Click **Actions** tab
3. See **Auto Version Bump** workflow running
4. Click on running workflow to see real-time logs

### After Workflow Completes
1. Go to **Actions** tab
2. See green checkmark ✓
3. Click workflow to see summary:
   ```
   ✅ All tests passed!
   Version bumped to: 1.0.1
   ```

## Version in Different Places

After auto-increment, version appears in:

| Location | How to Check | Shows |
|----------|--------------|-------|
| Python code | `from src import __version__` | `1.0.1` |
| Streamlit UI | Open app → Check sidebar | `v1.0.1` |
| Git tags | `git tag -l` | `v1.0.1` |
| GitHub releases | Releases tab | `v1.0.1` |
| PyProject | `cat pyproject.toml` | `version = "1.0.1"` |
| CHANGELOG | `cat CHANGELOG.md` | `## [1.0.1]` |

## Common Questions

**Q: Does every commit increment version?**  
A: Only commits to `master`/`main` that change source code AND pass all tests.

**Q: Can I skip auto-versioning for a commit?**  
A: Yes, add `[skip ci]` to commit message or modify only docs/tests.

**Q: What if I want to bump MAJOR or MINOR version?**  
A: Edit `src/__init__.py` and `pyproject.toml` manually, or modify `bump_version.py` script.

**Q: Can I see version history?**  
A: Yes, use `git tag -l "v*"` or check `CHANGELOG.md`.

**Q: What if two people push at the same time?**  
A: GitHub queues workflows, they run sequentially. Each gets its own version.

**Q: How do I revert to an old version?**  
A: `git checkout v1.0.5 -- src/__init__.py pyproject.toml`

**Q: Does this cost anything?**  
A: No, GitHub Actions is free for public repositories (2000 minutes/month for private).

## Summary

✨ **The Magic**:
1. You push code
2. Tests run automatically
3. If tests pass, version increments
4. Changes committed back
5. Git tag created
6. You pull and see new version

🎯 **The Result**:
- Every successful commit has unique version
- Only quality code (passing tests) gets versioned
- Complete audit trail via git tags
- Professional, industry-standard versioning
- Zero manual effort required

🚀 **What You Do**:
```bash
# Just normal git workflow:
git add .
git commit -m "your changes"
git push

# That's it! Version handles itself.
```
